from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import  QtCore
from PyQt5.QtOpenGL import QGLWidget
from PIL import Image
from io import BytesIO
from qgis.core import Qgis
import math
import requests

from .DBHandler import connector, connector_gpkg

class GLWidget(QGLWidget):
    def __init__(self, parent, iface, url, direction, map_manager, angle_degrees, x, y, params, gpkg, instance):
        super().__init__(parent)
        self.instance = instance
        self.show_crosshair = False
        self.url = url
        self.iface = iface
        self.x = x
        self.y = y
        self.direction = direction
        self.angle_degrees = angle_degrees
        self.params = params
        self.parent = parent
        try :
            if "http" in self.url :
                response = requests.get(self.url)
                self.image = Image.open(BytesIO(response.content))
            else :
                self.image = Image.open(self.url)
        except Exception:
            iface.messageBar().pushMessage("Unable to load the image, please verify image's source", level=Qgis.Info)
        self.image_width, self.image_height = self.image.size
        self.yaw = 90 - (direction - ((450 - angle_degrees) % 360))
        self.pitch = 0
        self.prev_dx = 0
        self.prev_dy = 0
        self.fov = 60
        self.moving = False
        self.direction = angle_degrees
        self.map_manager = map_manager
        self.gpkg = gpkg

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image_width, self.image_height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tobytes())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.sphere = gluNewQuadric()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, self.width()/self.height(), 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(90, 1, 0, 0)
        glRotatef(90, 0, 0, 1)
        gluQuadricTexture(self.sphere, True)
        gluSphere(self.sphere, 1, 100, 100)
        glPopMatrix()
        if self.show_crosshair:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, self.width(), self.height(), 0)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            glDisable(GL_DEPTH_TEST)
            glColor3f(1.0, 1, 1)
            glLineWidth(4.0)
            glBegin(GL_LINES)
            glVertex2f(self.width()/2 - 10, self.height()/2)
            glVertex2f(self.width()/2 + 10, self.height()/2)
            glVertex2f(self.width()/2, self.height()/2 - 10)
            glVertex2f(self.width()/2, self.height()/2 + 10)
            glEnd()
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width()/self.height(), 0.1, 1000)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.setCursor(QtCore.Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if self.moving == False :
            self.setCursor(QtCore.Qt.WaitCursor)
            try :
                x, y = self.recalculate_coordinates(self.x, self.y, self.direction, self.parent.gap_spinbox.value())
                self.x = x
                self.y = y
                if self.gpkg != True : 
                    self.img, self.dir, self.pointReal, self.year = connector(x, y, self.params)
                else  :
                    self.img, self.dir, self.pointReal, self.year = connector_gpkg(x, y, self.params)
                if self.img != self.url and self.img != 0 :
                    self.url  = self.img
                    if self.instance == 1 :
                        self.map_manager.remove_first_instance_points()
                        self.map_manager.add_point_to_map(self.pointReal, self.direction, self.instance)
                    else :
                        self.map_manager.remove_second_instance_points()
                        self.map_manager.add_point_to_map(self.pointReal, self.direction, self.instance)
                    self.yaw = 90 - (float(self.dir) - ((450 - self.direction) % 360))
                    if "http" in self.url :
                        response = requests.get(self.url)
                        self.image = Image.open(BytesIO(response.content))
                    else :
                        self.image = Image.open(self.url)
                    self.image_width, self.image_height = self.image.size
                    self.initializeGL()
                    self.paintGL()
                    self.resizeGL(self.width(), self.height())
                    self.update()
                else :
                    x, y = self.recalculate_coordinates(self.x, self.y, self.direction, -self.parent.gap_spinbox.value())
                    self.x = x
                    self.y = y
                    self.iface.messageBar().pushMessage("No image found", level=Qgis.Info)
            except Exception as e : 
                self.iface.messageBar().pushMessage(str(self.url), level=Qgis.Warning)
            finally : 
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
            self.yaw -= dx
            self.pitch -= dy
            self.pitch = min(max(self.pitch, -90), 90)
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.direction += dx
            self.map_manager.modify_line_direction(self.direction, self.instance)
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.fov -= delta * 0.1
        self.fov = max(30, min(self.fov, 90))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width()/self.height(), 0.1, 1000)
        self.update()

    def recalculate_coordinates(self, x, y, angle, distance):
        angle_rad = math.radians(angle)
        x_new = x + (distance * math.cos(angle_rad))
        y_new = y + (distance * math.sin(angle_rad))
        return x_new, y_new