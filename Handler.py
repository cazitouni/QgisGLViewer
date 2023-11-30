from qgis.PyQt.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget
from qgis.core import QgsWkbTypes, Qgis
from qgis.gui import QgsRubberBand, QgsMapTool
from qgis.PyQt.QtGui import QColor
import math

from .DBHandler import connector, connector_gpkg
from .Helpers import MapManager
from .Windows import MainWindow

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
        if self.gpkg is False :
            self.url, self.direction, self.pointReal, self.dates = connector(self.point.x(), self.point.y(), self.params)
        else :
            self.url, self.direction, self.pointReal, self.dates = connector_gpkg(self.point.x(), self.point.y(), self.params)

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
            self.dlg = MainWindow(self.iface, self.url, self.pointReal, map_manager, float(self.direction), angle_degrees, self.point.x(), self.point.y(), self.params, self.gpkg, self.dates)
            screen = QDesktopWidget().screenGeometry()
            size = self.dlg.geometry()
            x = (screen.width() - size.width()) / 2
            y = (screen.height() - size.height()) / 2
            self.dlg.move(int(x), int(y))
            self.dlg.show()
        self.iface.mapCanvas().unsetMapTool(self)

    def canvasMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            cursor_point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            self.rubberband.reset()
            self.rubberband.addPoint(self.point)
            self.rubberband.addPoint(cursor_point)
            self.point_rubberband.addPoint(self.point)