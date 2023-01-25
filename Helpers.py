from qgis.core import QgsPointXY, QgsWkbTypes, Qgis
from qgis.gui import QgsRubberBand, QgsMapTool
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget

import math

from .DBHandler import connector, connector_gpkg
from .Windows import MainWindow

class MapManager:
    def __init__(self, map_canvas):
        self.map_canvas = map_canvas
        self.rubberbands = []

    def add_point_to_map(self, point, direction):
        rb_line = QgsRubberBand(self.map_canvas, QgsWkbTypes.LineGeometry)
        rb_line.setColor(QColor(0, 0, 255))
        rb_line.setWidth(8)
        direction_on_map = direction
        x1 = point.x()
        y1 = point.y()
        x2 = x1 + 7 * math.cos(math.radians(direction_on_map))
        y2 = y1 + 7 * math.sin(math.radians(direction_on_map))
        rb_line.addPoint(QgsPointXY(x1, y1))
        rb_line.addPoint(QgsPointXY(x2, y2))
        rb_point = QgsRubberBand(self.map_canvas, QgsWkbTypes.PointGeometry)
        rb_point.setColor(QColor(255, 0, 0))
        rb_point.setWidth(10)
        rb_point.addPoint(QgsPointXY(point))
        self.rubberbands.extend([rb_line, rb_point])
        self.map_canvas.refresh()

    def modify_line_direction(self, new_direction):
        new_direction_on_map = new_direction
        line = self.rubberbands[0]
        start_point = line.getPoint(0)
        x1 = start_point.x()
        y1 = start_point.y()
        x2 = x1 + 7 * math.cos(math.radians(new_direction_on_map))
        y2 = y1 + 7 * math.sin(math.radians(new_direction_on_map))
        line.reset(QgsWkbTypes.LineGeometry)
        line.addPoint(QgsPointXY(x1, y1))
        line.addPoint(QgsPointXY(x2, y2))
        self.map_canvas.refresh()

    def remove_all_points_from_map(self):
        for rb in self.rubberbands:
            self.map_canvas.scene().removeItem(rb)
        self.rubberbands.clear()
        self.map_canvas.refresh()

class PointTool(QgsMapTool):
    def __init__(self, canvas, iface, params, gpkg):
        QgsMapTool.__init__(self, canvas)
        self.iface = iface
        self.canvas = canvas
        self.params = params
        self.point = None
        self.gpkg = gpkg
        self.direction = None
        self.rubberband = QgsRubberBand(self.canvas)
        self.rubberband.setColor(QColor(0, 0, 255))
        self.rubberband.setWidth(8)
        self.point_rubberband = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        self.point_rubberband.setColor(QColor(255, 0, 0))
        self.point_rubberband.setWidth(10)

    def canvasPressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        self.point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        if self.gpkg is not True :
            self.url, self.direction, self.pointReal, self.year = connector(self.point.x(), self.point.y(), self.params)
        else :
            self.url, self.direction, self.pointReal, self.year = connector_gpkg(self.point.x(), self.point.y(), self.params)

    def canvasReleaseEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        self.rubberband.reset()
        self.point_rubberband.reset()
        release_point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        angle = math.atan2(release_point.y() - self.point.y(), release_point.x() - self.point.x())
        if release_point.y() < self.point.y():
            angle += 2 * math.pi
        angle_degrees = (angle * 180 / math.pi)
        if self.url != 0 and self.direction is not None :
            map_manager = MapManager(self.canvas)
            map_manager.add_point_to_map(self.pointReal, angle_degrees)
            try :
                self.dlg = MainWindow(self.iface, self.url, map_manager, float(self.direction), angle_degrees, self.year, self.point.x(), self.point.y(), self.params, self.gpkg)
            except Exception :
                map_manager.remove_all_points_from_map()
                return
            screen = QDesktopWidget().screenGeometry()
            size = self.dlg.geometry()
            x = (screen.width() - size.width()) / 2
            y = (screen.height() - size.height()) / 2
            self.dlg.move(int(x), int(y))
            self.dlg.show()
            self.iface.mapCanvas().unsetMapTool(self)
        else :
            self.iface.messageBar().pushMessage("No image for this coordinates", level=Qgis.Info)

    def canvasMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            cursor_point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            self.rubberband.reset()
            self.rubberband.addPoint(self.point)
            self.rubberband.addPoint(cursor_point)
            self.point_rubberband.addPoint(self.point)