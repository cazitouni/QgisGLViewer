from qgis.core import QgsPointXY, QgsWkbTypes, QgsFeature
from qgis.gui import QgsRubberBand
from qgis.PyQt.QtGui import QColor

import math
import uuid

class MapManager:
    instances = []
    def __init__(self, map_canvas):
        MapManager.instances.append(self)
        self.map_canvas = map_canvas
        self.rubberbands = []
        self.crosspoints = []
        self.new_direction_on_map = None
        self.new_direction_on_map2 = None
        self.new_length = None
        self.init1 = 0
        self.init2 = 0

    def add_point_to_map(self, point, direction, instance):
        rb_line = QgsRubberBand(self.map_canvas, QgsWkbTypes.LineGeometry)
        if instance == 2 :
            rb_line.setColor(QColor(255, 165, 0))
        else :
            rb_line.setColor(QColor(0, 0, 255))
        rb_line.setWidth(8)
        self.direction_on_map = direction
        x1 = point.x()
        y1 = point.y()
        self.distance = 5
        if self.new_length is not None :
            dx = self.new_length * math.cos(math.radians(self.direction_on_map))
            dy = self.new_length * math.sin(math.radians(self.direction_on_map))
        else :
            dx = self.distance * math.cos(math.radians(self.direction_on_map))
            dy = self.distance * math.sin(math.radians(self.direction_on_map))
        x2 = x1 + dx
        y2 = y1 + dy
        rb_line.addPoint(QgsPointXY(x1, y1))
        rb_line.addPoint(QgsPointXY(x2, y2))
        rb_point = QgsRubberBand(self.map_canvas, QgsWkbTypes.PointGeometry)
        rb_point.setColor(QColor(255, 0, 0))
        rb_point.setWidth(10)
        rb_point.addPoint(QgsPointXY(point))
        if instance == 1 :
            self.rubberbands.insert(0, rb_line)
            self.rubberbands.insert(1, rb_point)
            self.init1 += 1
            self.ogdir1 = direction
        if instance == 2 :
            self.rubberbands.insert(2, rb_line)
            self.rubberbands.insert(3, rb_point)
            self.init2 += 1
            self.ogdir2 = direction
        self.map_canvas.refresh()

    def modify_line_direction(self, new_direction, instance):
        if instance == 1 :
            line = self.rubberbands[0]
            self.new_direction_on_map = new_direction
        elif instance == 2 :
            line = self.rubberbands[2]
            self.new_direction_on_map2 = new_direction
        start_point = line.getPoint(0)
        x1 = start_point.x()
        y1 = start_point.y()
        if instance == 1 :
            if self.new_length is not None :
                x2 = x1 + self.new_length * math.cos(math.radians(self.new_direction_on_map))
                y2 = y1 + self.new_length * math.sin(math.radians(self.new_direction_on_map))
            else :
                x2 = x1 + self.distance * math.cos(math.radians(self.new_direction_on_map))
                y2 = y1 + self.distance * math.sin(math.radians(self.new_direction_on_map))
        else :
            if self.new_length is not None :
                x2 = x1 + self.new_length * math.cos(math.radians(self.new_direction_on_map2))
                y2 = y1 + self.new_length * math.sin(math.radians(self.new_direction_on_map2))
            else :
                x2 = x1 + self.distance * math.cos(math.radians(self.new_direction_on_map2))
                y2 = y1 + self.distance * math.sin(math.radians(self.new_direction_on_map2))
        line.reset(QgsWkbTypes.LineGeometry)
        line.addPoint(QgsPointXY(x1, y1))
        line.addPoint(QgsPointXY(x2, y2))
        self.map_canvas.refresh()

    def modify_line_length(self, new_length):
        self.new_length = new_length
        line = self.rubberbands[0]
        start_point = line.getPoint(0)
        x1 = start_point.x()
        y1 = start_point.y()
        if self.new_direction_on_map is not None : 
            x2 = x1 + new_length * math.cos(math.radians(self.new_direction_on_map))
            y2 = y1 + new_length * math.sin(math.radians(self.new_direction_on_map))
        elif self.init1 == 1 and self.new_direction_on_map is None : 
            x2 = x1 + new_length * math.cos(math.radians(self.ogdir1))
            y2 = y1 + new_length * math.sin(math.radians(self.ogdir1))
        else :
            x2 = x1 + new_length * math.cos(math.radians(self.direction_on_map))
            y2 = y1 + new_length * math.sin(math.radians(self.direction_on_map))
        line.reset(QgsWkbTypes.LineGeometry)
        line.addPoint(QgsPointXY(x1, y1))
        line.addPoint(QgsPointXY(x2, y2))
        self.map_canvas.refresh()

        if len(self.rubberbands) == 4 : 
            line = self.rubberbands[2]
            start_point = line.getPoint(0)
            x1 = start_point.x()
            y1 = start_point.y()
            if self.new_direction_on_map2 is not None : 
                x2 = x1 + new_length * math.cos(math.radians(self.new_direction_on_map2))
                y2 = y1 + new_length * math.sin(math.radians(self.new_direction_on_map2))
            elif self.init2 == 1 and self.new_direction_on_map2 is None : 
                x2 = x1 + new_length * math.cos(math.radians(self.ogdir2))
                y2 = y1 + new_length * math.sin(math.radians(self.ogdir2))
            else : 
                x2 = x1 + new_length * math.cos(math.radians(self.direction_on_map))
                y2 = y1 + new_length * math.sin(math.radians(self.direction_on_map))
            line.reset(QgsWkbTypes.LineGeometry)
            line.addPoint(QgsPointXY(x1, y1))
            line.addPoint(QgsPointXY(x2, y2))
            self.map_canvas.refresh()

    def remove_all_crosspoints_from_map(self):
        for pt in self.crosspoints:
            self.map_canvas.scene().removeItem(pt)
        self.crosspoints.clear()
        self.map_canvas.refresh()

    def remove_all_points_from_map(self):
        for rb in self.rubberbands:
            self.map_canvas.scene().removeItem(rb)
        self.rubberbands.clear()
        self.map_canvas.refresh()
    
    def remove_first_instance_points(self):
        for rb in self.rubberbands[0:2]:
            self.map_canvas.scene().removeItem(rb)
        del self.rubberbands[0:2]
        self.map_canvas.refresh()
    
    def remove_second_instance_points(self):
        for rb in self.rubberbands[2:4]:
            self.map_canvas.scene().removeItem(rb)
        del self.rubberbands[2:4]
        self.map_canvas.refresh()

    def check_for_crossing_lines(self):
        if len(self.rubberbands) < 4:
            return False
        line1_geometry = self.rubberbands[0].asGeometry()
        line2_geometry = self.rubberbands[2].asGeometry()
        line1_start = None
        line1_end = None
        line2_start = None
        line2_end = None
        for vertex in line1_geometry.vertices():
            if line1_start is None:
                line1_start = QgsPointXY(vertex)
            else:
                line1_end = QgsPointXY(vertex)
        for vertex in line2_geometry.vertices():
            if line2_start is None:
                line2_start = QgsPointXY(vertex)
            else:
                line2_end = QgsPointXY(vertex)
        p1 = line1_start
        p2 = line1_end
        p3 = line2_start
        p4 = line2_end
        d = (p4.y() - p3.y()) * (p2.x() - p1.x()) - (p4.x() - p3.x()) * (p2.y() - p1.y())
        if d == 0:
            return False
        else:
            ua = ((p4.x() - p3.x()) * (p1.y() - p3.y()) - (p4.y() - p3.y()) * (p1.x() - p3.x())) / d
            ub = ((p2.x() - p1.x()) * (p1.y() - p3.y()) - (p2.y() - p1.y()) * (p1.x() - p3.x())) / d
            if ua >= 0 and ua <= 1 and ub >= 0 and ub <= 1:
                intersection_point = QgsPointXY(p1.x() + ua * (p2.x() - p1.x()), p1.y() + ua * (p2.y() - p1.y()))
                rb_point = QgsRubberBand(self.map_canvas, QgsWkbTypes.PointGeometry)
                rb_point.setColor(QColor(0, 128, 0))
                rb_point.setWidth(10)
                rb_point.addPoint(intersection_point)
                self.crosspoints.append(rb_point)
                self.map_canvas.refresh()
                return True
            else:
                return False

    def export_crosspoints_to_vlayer(self, layer):
        layerProvider = layer.dataProvider()
        for i, point in enumerate(self.crosspoints):
            feature = QgsFeature()
            geometry = point.asGeometry()
            feature.setGeometry(geometry)
            feature.setAttributes([str(uuid.uuid4()), point.x(), point.y()])
            layerProvider.addFeature(feature)
        layer.updateExtents()