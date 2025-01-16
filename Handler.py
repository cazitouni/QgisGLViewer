import math

from PyQt5.QtWidgets import QDesktopWidget
from qgis.core import Qgis, QgsWkbTypes
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor

from .DBHandler import connector, connector_gpkg, connector_panoramax
from .Helpers import MapManager
from .Windows import MainWindow


class PointTool(QgsMapTool):
    def __init__(self, canvas, iface, params, conntype):
        QgsMapTool.__init__(self, canvas)
        self.iface = iface
        self.canvas = canvas
        self.params = params
        self.point = None
        self.conntype = conntype
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
        if self.conntype == "PostGIS":
            (
                self.url,
                self.direction,
                self.pointReal,
                self.dates,
                self.message,
                self.index,
            ) = connector(self.point.x(), self.point.y(), self.params)
        elif self.conntype == "Geopackage":
            (
                self.url,
                self.direction,
                self.pointReal,
                self.dates,
                self.message,
                self.index,
            ) = connector_gpkg(self.point.x(), self.point.y(), self.params)
        elif self.conntype == "Panoramax":
            (
                self.url,
                self.direction,
                self.pointReal,
                self.dates,
                self.message,
                self.index,
            ) = connector_panoramax(self.point.x(), self.point.y(), self.params)

    def canvasReleaseEvent(self, event):
        self.iface.mapCanvas().unsetMapTool(self)
        x = event.pos().x()
        y = event.pos().y()
        self.rubberband.reset()
        self.point_rubberband.reset()
        release_point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        angle = math.atan2(
            release_point.y() - self.point.y(), release_point.x() - self.point.x()
        )
        if release_point.y() < self.point.y():
            angle += 2 * math.pi
        angle_degrees = angle * 180 / math.pi
        if self.url != 0 and self.direction is not None:
            map_manager = MapManager(self.canvas)
            self.dlg = MainWindow(
                self.iface,
                self.url,
                self.pointReal,
                map_manager,
                float(self.direction),
                angle_degrees,
                self.point.x(),
                self.point.y(),
                self.params,
                self.conntype,
                self.dates,
                self.index,
            )
            screen = QDesktopWidget().screenGeometry()
            size = self.dlg.geometry()
            x = (screen.width() - size.width()) / 2
            y = (screen.height() - size.height()) / 2
            self.dlg.move(int(x), int(y))
            self.dlg.show()
        else:
            self.iface.messageBar().pushMessage(
                "Unable to fetch the image from the database",
                self.message,
                level=Qgis.Warning,
            )

    def canvasMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            cursor_point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            self.rubberband.reset()
            self.rubberband.addPoint(self.point)
            self.rubberband.addPoint(cursor_point)
            self.point_rubberband.addPoint(self.point)
