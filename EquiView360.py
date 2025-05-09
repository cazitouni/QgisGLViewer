import datetime
import math
import os
from io import BytesIO

import requests
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_LINEAR,
    GL_LINES,
    GL_MODELVIEW,
    GL_PROJECTION,
    GL_RGBA,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_UNSIGNED_BYTE,
    glBegin,
    glBindTexture,
    glClear,
    glClearColor,
    glColor3f,
    glEnable,
    glEnd,
    glGenerateMipmap,
    glGenTextures,
    glLineWidth,
    glLoadIdentity,
    glMatrixMode,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glTexImage2D,
    glTexParameteri,
    glVertex2f,
    glViewport,
)
from OpenGL.GLU import (
    gluNewQuadric,
    gluOrtho2D,
    gluPerspective,
    gluQuadricTexture,
    gluSphere,
)
from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QOpenGLWidget
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsProject,
    QgsUnitTypes,
)

from .DBHandler import connector, connector_gpkg, connector_panoramax


class GLWidget(QOpenGLWidget):
    def __init__(
        self,
        parent,
        iface,
        url,
        direction,
        map_manager,
        angle_degrees,
        x,
        y,
        params,
        conntype,
        instance,
    ):
        format = QSurfaceFormat()
        format.setProfile(QSurfaceFormat.CompatibilityProfile)
        QSurfaceFormat.setDefaultFormat(format)
        super().__init__(parent)
        self.instance = instance
        self.show_crosshair = False
        self.url = url
        self.iface = iface
        self.x = x
        self.y = y
        self.prev_dx = 0
        self.prev_dy = 0
        self.direction = direction
        self.angle_degrees = angle_degrees
        self.params = params
        self.parent = parent
        self.parent.comboBox1.currentIndexChanged.connect(
            lambda index: self.date_change(self.parent.comboBox1.currentText())
        )
        try:
            if "http" in self.url:
                response = requests.get(self.url)
                self.image = Image.open(BytesIO(response.content))
            else:
                if self.url.startswith("./"):
                    self.url = self.url[1:]
                    project_path = os.path.dirname(QgsProject.instance().fileName())
                    self.url = project_path + self.url
                self.image = Image.open(self.url)
        except Exception:
            iface.messageBar().pushMessage(
                "Unable to load the image, please verify image's source",
                level=Qgis.Info,
            )
        self.image_width, self.image_height = self.image.size
        self.yaw = 90 - (direction - ((450 - angle_degrees) % 360))
        self.pitch = 0
        self.sensitivity = 1
        self.fov = 60
        self.moving = False
        self.direction = angle_degrees
        self.map_manager = map_manager
        self.conntype = conntype

    def load_texture(self):
        try:
            if "http" in self.url:
                response = requests.get(self.url)
                image = Image.open(BytesIO(response.content))
            else:
                if self.url.startswith("./"):
                    self.url = self.url[1:]
                    project_path = os.path.dirname(QgsProject.instance().fileName())
                    self.url = project_path + self.url
                image = Image.open(self.url)

            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = image.tobytes("raw", "RGBX", 0, -1)
            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                image.width,
                image.height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                img_data,
            )
            glGenerateMipmap(GL_TEXTURE_2D)

        except Exception as e:
            print(f"Texture loading error: {e}")

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        self.load_texture()
        self.setup_projection()

    def setup_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, self.width() / self.height(), 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)
        self.render_scene()

    def render_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        self.apply_rotation()
        self.draw_sphere()
        glPopMatrix()
        self.draw_crosshair_if_required()

    def apply_rotation(self):
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(90, 1, 0, 0)
        glRotatef(90, 0, 0, 1)

    def draw_sphere(self):
        if hasattr(self, "texture_id"):
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        else:
            print("No texture loaded, drawing without texture.")
        sphere = gluNewQuadric()
        gluQuadricTexture(sphere, True)
        gluSphere(sphere, 1, 100, 100)

    def draw_crosshair_if_required(self):
        if self.show_crosshair:
            self.draw_crosshair()

    def draw_crosshair(self):
        crosshair_size = 30
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width(), self.height(), 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(0, 0, 0)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex2f(self.width() / 2 - crosshair_size / 2, self.height() / 2)
        glVertex2f(self.width() / 2 + crosshair_size / 2, self.height() / 2)
        glEnd()
        glBegin(GL_LINES)
        glVertex2f(self.width() / 2, self.height() / 2 - crosshair_size / 2)
        glVertex2f(self.width() / 2, self.height() / 2 + crosshair_size / 2)
        glEnd()
        glColor3f(1.0, 1.0, 1.0)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.setCursor(QtCore.Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if not self.moving:
            self.setCursor(QtCore.Qt.WaitCursor)
            x, y = self.recalculate_coordinates(
                self.x, self.y, self.direction, self.parent.gap_spinbox.value()
            )
            self.x = x
            self.y = y
            if self.conntype == "PostGIS":
                self.img, self.dir, self.pointReal, dates, _, index = connector(
                    x, y, self.params, self.parent.comboBox1.currentText()
                )
            elif self.conntype == "Geopackage":
                self.img, self.dir, self.pointReal, dates, _, index = connector_gpkg(
                    x, y, self.params, self.parent.comboBox1.currentText()
                )
            else:
                self.img, self.dir, self.pointReal, dates, _, index = (
                    connector_panoramax(
                        x, y, self.params, self.parent.comboBox1.currentText()
                    )
                )
            if self.img != self.url and self.img != 0:
                self.url = self.img
                if self.instance == 1:
                    self.map_manager.remove_first_instance_points()
                    self.map_manager.add_point_to_map(
                        self.pointReal, self.direction, self.instance
                    )
                else:
                    self.map_manager.remove_second_instance_points()
                    self.map_manager.add_point_to_map(
                        self.pointReal, self.direction, self.instance
                    )
                self.yaw = 90 - (float(self.dir) - ((450 - self.direction) % 360))
                if "http" in self.url:
                    response = requests.get(self.url)
                    image_source = BytesIO(response.content)
                else:
                    if self.url.startswith("./"):
                        self.url = self.url[1:]
                        project_path = os.path.dirname(QgsProject.instance().fileName())
                        self.url = project_path + self.url
                    image_source = self.url
                with Image.open(image_source) as image:
                    self.image_width, self.image_height = image.size
                    self.initializeGL()
                    self.paintGL()
                    self.resizeGL(self.width(), self.height())
                    self.update()
            else:
                x, y = self.recalculate_coordinates(
                    self.x, self.y, self.direction, -self.parent.gap_spinbox.value()
                )
                self.x = x
                self.y = y
                self.iface.messageBar().pushMessage("No image found", level=Qgis.Info)
            if dates is not None:
                self.parent.comboBox1.currentIndexChanged.disconnect()
                self.parent.comboBox1.clear()
                for date in dates:
                    if type(date) is QtCore.QDate or type(date) is QtCore.QDateTime:
                        date = date.toString()
                    elif isinstance(date, datetime.datetime):
                        date = date.strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(date, datetime.date):
                        date = date.strftime("%Y-%m-%d")
                    self.parent.comboBox1.addItem(date)
            if index:
                self.parent.comboBox1.setCurrentIndex(index)
            self.parent.comboBox1.currentIndexChanged.connect(
                lambda index: self.date_change(self.parent.comboBox1.currentText())
            )
            self.setCursor(QtCore.Qt.OpenHandCursor)
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.OpenHandCursor)
            self.moving = False

    def mouseMoveEvent(self, event):
        self.moving = True
        if self.moving:
            dx = event.pos().x() - self.mouse_x
            dy = event.pos().y() - self.mouse_y
            dx *= 0.1
            dy *= 0.1
            self.yaw -= dx * self.sensitivity
            self.pitch -= dy * self.sensitivity
            self.pitch = min(max(self.pitch, -90), 90)
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.direction += dx
            self.map_manager.modify_line_direction(self.direction, self.instance)
            self.update()
        self.prev_dx = dx
        self.prev_dy = dy

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.fov -= delta * 0.1
        self.fov = max(30, min(self.fov, 90))
        self.sensitivity = self.fov / 60
        self.update()

    def recalculate_coordinates(self, x, y, angle, distance):
        angle_rad = math.radians(angle)
        point = QgsPointXY(x, y)
        if QgsProject.instance().crs().mapUnits() == QgsUnitTypes.DistanceDegrees:
            src_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            dst_crs = QgsCoordinateReferenceSystem("EPSG:3857")
            transform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())
            untransform = QgsCoordinateTransform(
                dst_crs, src_crs, QgsProject.instance()
            )
            point = transform.transform(point)

        x_new = point.x() + (distance * math.cos(angle_rad))
        y_new = point.y() + (distance * math.sin(angle_rad))
        if QgsProject.instance().crs().mapUnits() == QgsUnitTypes.DistanceDegrees:
            point = QgsPointXY(x_new, y_new)
            point = untransform.transform(point)
            x_new = point.x()
            y_new = point.y()
        return x_new, y_new

    def date_change(self, date_selected):
        self.setCursor(QtCore.Qt.WaitCursor)
        if self.conntype == "PostGIS":
            self.img, self.dir, self.pointReal, self.dates, _, _ = connector(
                self.x, self.y, self.params, date_selected
            )
        elif self.conntype == "Geopackage":
            self.img, self.dir, self.pointReal, self.dates, _, _ = connector_gpkg(
                self.x, self.y, self.params, date_selected
            )
        else:
            self.img, self.dir, self.pointReal, self.dates, message, _ = (
                connector_panoramax(self.x, self.y, self.params, date_selected)
            )
        if self.img != self.url and self.img != 0:
            self.url = self.img
            self.map_manager.remove_first_instance_points()
            self.map_manager.add_point_to_map(
                self.pointReal, self.direction, self.instance
            )
            self.yaw = 90 - (float(self.dir) - ((450 - self.direction) % 360))
            if "http" in self.url:
                response = requests.get(self.url)
                image_source = BytesIO(response.content)
            else:
                if self.url.startswith("./"):
                    self.url = self.url[1:]
                    project_path = os.path.dirname(QgsProject.instance().fileName())
                    self.url = project_path + self.url
                image_source = self.url
            with Image.open(image_source) as image:
                self.image_width, self.image_height = image.size
                self.initializeGL()
                self.paintGL()
                self.resizeGL(self.width(), self.height())
                self.update()
        self.setCursor(QtCore.Qt.OpenHandCursor)
