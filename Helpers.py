from qgis.core import QgsPointXY
from qgis.gui import QgsVertexMarker
from qgis.PyQt.QtGui import QColor

class MapManager:
    def __init__(self, map_canvas):
        self.map_canvas = map_canvas
        self.markers = []
    
    def add_point_to_map(self, point, direction):
        m1 = QgsVertexMarker(self.map_canvas)
        m2 = QgsVertexMarker(self.map_canvas)
        m1.setCenter(QgsPointXY(point))
        m2.setCenter(QgsPointXY(point))
        m1.setColor(QColor(255,0, 0))
        m2.setColor(QColor(0,0, 255))
        m1.setFillColor(QColor(255,0, 0))
        m1.setIconSize(10)
        m2.setIconSize(50)
        m1.setIconType(QgsVertexMarker.ICON_CIRCLE)
        m2.setIconType(QgsVertexMarker.ICON_INVERTED_TRIANGLE)
        m1.setPenWidth(3)
        m2.setPenWidth(3)
        self.markers.append(m1)
        self.markers.append(m2)
        self.map_canvas.refresh()
        
    def remove_all_points_from_map(self):
        for mark in self.markers : 
         self.map_canvas.scene().removeItem(mark)
        self.map_canvas.refresh()