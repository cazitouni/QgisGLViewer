from qgis.core import QgsPointXY, QgsWkbTypes, Qgis
from qgis.gui import QgsRubberBand, QgsMapTool
from qgis.PyQt.QtGui import QColor
from PyQt5.QtWidgets import QDesktopWidget

import math

from .DBHandler import connector
from .Windows import MainWindow

class MapManager:
    def __init__(self, map_canvas):
        self.map_canvas = map_canvas
        self.rubberbands = []

    def add_point_to_map(self, point, direction):
        rb_line = QgsRubberBand(self.map_canvas, QgsWkbTypes.LineGeometry)
        rb_line.setColor(QColor(0, 0, 255))
        rb_line.setWidth(8)
        direction_on_map = 90 - direction
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
        new_direction_on_map = 90 - new_direction
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

    def __init__(self, canvas, iface, cursor, geom, yaw, link, schema, table):
        QgsMapTool.__init__(self, canvas)
        self.iface = iface
        self.canvas = canvas
        self.cursor = cursor
        self.schema = schema
        self.table = table
        self.link = link
        self.geom = geom
        self.yaw = yaw
        self.direction = None
        
    def canvasPressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        url, direction, pointReal = connector(point.x(), point.y(), self.cursor, self.geom, self.schema, self.table, self.link, self.yaw)
        if url != 0 and direction is not None :
            map_manager = MapManager(self.canvas)
            map_manager.add_point_to_map(pointReal, float(direction))
            self.dlg = MainWindow(self.iface, url, map_manager, float(direction))
            screen = QDesktopWidget().screenGeometry()
            size = self.dlg.geometry()
            x = (screen.width() - size.width()) / 2
            y = (screen.height() - size.height()) / 2
            self.dlg.move(int(x), int(y))
            self.dlg.show()
            self.iface.mapCanvas().unsetMapTool(self)
        else : 
            self.iface.messageBar().pushMessage("No image for this coordinates", level=Qgis.Info)