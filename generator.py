
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import gdspy
import math
import importlib.util

um           = 1
mm           = 1000*um
wafer_rad    = 75.0*mm
ebr          = 3*mm
flat_exclude = 5*mm
flat_dist           = 69.27*mm
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        factor     = 0.005
        self.view  = DiagramView()
        self.scene = DiagramScene()
        self.scene.setSceneRect(-wafer_rad*2, -wafer_rad*2, 4*wafer_rad, 4*wafer_rad)
        self.view.scale(1*factor, -1*factor)
        
        self.view.setScene(self.scene)
        self.view.show()
        
        v = QVBoxLayout()
        v.addWidget(self.view)
        self.setLayout(v)
        self.m()
        self.view.centerOn (0,0)
        self.showMaximized()
        self.view.setRenderHints (QPainter.HighQualityAntialiasing | QPainter.SmoothPixmapTransform)
    
    def new_shot(self, x, y, row, column, die_width, die_height):
        die_array = []
        for c in range(column):
            for r in range(row):
                x, y, w, h = c * die_width, r * die_height, die_width, die_height
                die_array.append(die_item(x, y, w, h))

        group = self.scene.createItemGroup(die_array)
        # group.translate(x, y)
        return group
            
        



    def m(self):

        
        ebr          = 3*mm
        flat_exclude = 10*mm

        row    = 11
        column = 15
        die_w  = 1000*um
        die_h  = 1200*um
        step_x = die_w*column
        step_y = die_h*row
        offset_x = -step_x/2
        offset_y = -750*um
        wafer = wafer_item(wafer_rad)
        shot_array = []
        for c in range(int(((wafer_rad-ebr+offset_x)/step_x)+1)*-1, int(((wafer_rad-ebr+offset_x)/step_x)+2)):
            column_array = []
            for r in range(-int(((wafer_rad-flat_exclude)/step_y) + 1),  int(((wafer_rad-ebr)/step_y) + 1)):
                column_array.append(shot_item(offset_x + (step_x*c), offset_y + (step_y*r), row, column, die_w, die_h, wafer))
            shot_array.append(column_array)

        for column_array in shot_array:
            n = 0
            for shot in column_array:
                if wafer.in_zero_range(shot.boundingRect()) == wafer_item.fully_in_range: 
                    n=1
                shot = shot.shift_by_die(0, 5*n)                    
                if not wafer.in_ebr_range(shot.boundingRect()) == wafer_item.not_in_range:
                    self.scene.addItem(shot)


        
        self.scene.addItem(origin_item(offset_x, offset_y))
        self.scene.addItem(asml_ak_item(-45*mm, 0))
        self.scene.addItem(asml_ak_item( 45*mm, 0))
        self.scene.addItem(wafer)
        # self.scene.addItem(ebr_item(ebr= ebr, flat_exclude= flat_exclude))
        




class shot_item(QGraphicsItem):

    def __init__(self, x, y, row, column, die_width, die_height, wafer, parent=None):
        super(shot_item, self).__init__(parent)
        self._wafer      = wafer
        self._x          = x
        self._y          = y
        self._die_width  = die_width
        self._die_height = die_height
        self._row        = row
        self._column     = column
        self._w          = self._die_width  * self._column
        self._h          = self._die_height * self._row
        self._gross_die  = []
        self._dummy_die  = []

        self._shot_pen   = QPen(QColor('#444444'), 1, Qt.SolidLine)
        self._shot_brush = QBrush(Qt.NoBrush)
        self._die_pen         = QPen(QColor('#dadada'), 1, Qt.SolidLine)
        self._shot_pen.setCosmetic(True)
        self._die_pen.setCosmetic(True)
        self._dummy_die_brush = QBrush(Qt.NoBrush)
        self._gross_die_brush = QBrush(QColor('#777777'), Qt.SolidPattern)

    def shift(self, dx, dy):
        self._x += dx
        self._y += dy
        return self

    def shift_by_die(self, dx, dy):
        return self.shift(dx * self._die_width, dy * self._die_height)

    
    def draw_dies(self, painter):
        for column in range(self._column):
            for row in range(self._row):
                x, y, w, h = self._x + (column * self._die_width), self._y +( row * self._die_height), self._die_width, self._die_height
                rect = QRectF(x, y, w, h)
                painter.setPen( self._die_pen)
                painter.setBrush( self._gross_die_brush if self._wafer.in_ebr_range(rect) == wafer_item.fully_in_range else self._dummy_die_brush)
                painter.drawRect(rect)


    def boundingRect(self):
        return QRectF(self._x, self._y, self._w, self._h)

    def paint(self, painter, option, widget):
        self.draw_dies(painter)
        painter.setPen(self._shot_pen)
        painter.setBrush(self._shot_brush)
        painter.drawRect(QRectF(self._x, self._y, self._w, self._h))

class die_item(QGraphicsItem):
    def __init__(self, x, y, die_width, die_height, dummy_die_brush, gross_die_brush, die_pen, parent=None):
        super(die_item, self).__init__(parent)
        
        self._x               = x
        self._y               = y
        self._w               = die_width
        self._h               = die_height
        self.valid            = ((x**2) + (y**2))**(0.5) <= wafer_rad
        self._dummy_die_brush = dummy_die_brush
        self._gross_die_brush = gross_die_brush
        self._current_brush   = self._gross_die_brush if self.valid else self._dummy_die_brush
        self._die_pen         = die_pen

    
        self._rect = QRectF(x, y, die_width, die_height)

    def paint(self, painter, option, widget):       
        painter.setPen(self._die_pen)
        painter.setBrush(self._current_brush)
        painter.drawRect(self.boundingRect())

    def boundingRect(self):
        return QRectF(self._x, self._y, self._w, self._h)

class origin_item(QGraphicsItem):
    def __init__(self, x, y, w = 800*um, h =800*um, parent=None):
        super(origin_item, self).__init__(parent)    
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    def paint(self, painter, option, widget):
        pen   = QPen(Qt.NoPen)
        brush = QBrush(QColor("#ff0000"), Qt.SolidPattern)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(self._x-(self._w/2), self._y-(self._h/2), self._w, self._h)

    def boundingRect(self):
        return QRectF(self._x-(self._w/2), self._y-(self._h/2), self._w, self._h)

  

class wafer_item(QGraphicsItem):
    fully_in_range    = 0x11
    partilly_in_range = 0x10
    not_in_range      = 0x00
    def __init__(self, radius = wafer_rad, parent=None):
        super(wafer_item, self).__init__(parent)
        self._radius              = 75.00*mm
        self._flat_length         = 57.50*mm
        self._flat_theta          = 0.39340  #math.asin((self._flat_length/2) / self._radius)
        self._flat_dist           = 69.27*mm #self._radius * math.cos(self._flat_theta)   
        self._ebr_width           = ebr
        self._flat_exclude        = flat_exclude
        self._exclude_theta       = math.acos((self._flat_dist-self._flat_exclude)/(self._radius-self._ebr_width))
        self._exclude_flat_length = (self._radius-self._ebr_width)*math.sin(self._exclude_theta)*2
        self._x                   = -radius
        self._y                   = -radius
        self._w                   = radius *2
        self._h                   = radius *2        
        self._cx                  = self._x + self._w /2
        self._cy                  = self._y + self._h /2

        points = 50
        delta_theta1= ((2 * math.pi) - (2 * self._flat_theta))/points
        self.pts = []
        delta_theta2= ((2 * math.pi) - (2 * self._exclude_theta))/points
        self.pts2 = []        
        for  i in range(points+1):
            theta = 1.5 * math.pi + self._flat_theta + delta_theta1 * i
            self.pts.append(QPointF(radius * math.cos(theta), radius * math.sin(theta)))
            theta = 1.5 * math.pi + self._exclude_theta + delta_theta2 * i
            self.pts2.append(QPointF((radius-self._ebr_width) * math.cos(theta), (radius-self._ebr_width) * math.sin(theta)))


        self._pen   = QPen(QColor('#444444'), .5, Qt.SolidLine)
        self._pen.setCosmetic(True)
        self._brush = QBrush(Qt.NoBrush)    

    def paint(self, painter, option, widget):
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawPolygon(QPolygonF(self.pts))
        painter.drawPolygon(QPolygonF(self.pts2))


        # painter.drawLine(self._cx - self._flat_length/2, self._cy - self._flat_dist, self._cx + self._flat_length/2 , self._cy - self._flat_dist)


    def boundingRect(self):
        return QRectF(self._x, self._y, self._w, self._h)

    def in_ebr_range(self, rect):
        wafer_rad, ebr, flat_dist,  flat_exclude = self._radius, self._ebr_width, self._flat_dist,  self._flat_exclude
        u, d, l, r = rect.bottom(), rect.top(), rect.left(), rect.right()
        detection = [
            ((d-self._cy)**2 + (l-self._cx)**2) <= (wafer_rad - ebr) **2 and (d-self._cy) >= -flat_dist + flat_exclude, 
            ((u-self._cy)**2 + (l-self._cx)**2) <= (wafer_rad - ebr) **2 and (u-self._cy) >= -flat_dist + flat_exclude, 
            ((d-self._cy)**2 + (r-self._cx)**2) <= (wafer_rad - ebr) **2 and (d-self._cy) >= -flat_dist + flat_exclude,
            ((u-self._cy)**2 + (r-self._cx)**2) <= (wafer_rad - ebr) **2 and (u-self._cy) >= -flat_dist + flat_exclude
        ]
        if all(detection):
            return wafer_item.fully_in_range
        elif any(detection):
            return wafer_item.partilly_in_range
        else:
            return wafer_item.not_in_range

    def in_zero_range(self, rect):
        u, d, l, r = rect.bottom(), rect.top(), rect.left(), rect.right()
        
        if (u >=0 and  d <= 0 and l <= -45*mm and r >= -45*mm) or (u >=0 and  d <= 0 and l <= 45*mm and r >= 45*mm):
            return wafer_item.fully_in_range
        else: 
            return wafer_item.not_in_range



class asml_ak_item(QGraphicsItem):
    def __init__(self, x, y, w = 800*um, h = 800*um, parent=None):
        super(asml_ak_item, self).__init__(parent)
        self._x = x -w/2
        self._y = y -h/2
        self._w = w
        self._h = h

        self._pen   = QPen(Qt.NoPen)
        self._brush = QBrush(QColor("#444444"), Qt.SolidPattern)    

    def paint(self, painter, option, widget):
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawRect(self.boundingRect())

    def boundingRect(self):
        return QRectF(self._x, self._y, self._w, self._h) 

class DiagramView(QGraphicsView):
    def __init__(self, parent=None):
        super(DiagramView, self).__init__(parent)        
        self.init_ui()
        self._zoom = 1

    def init_ui(self):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor("#ffffff")))
        self.setFrameShape(QFrame.NoFrame)



    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        # if self._zoom > 0:
        self.scale(factor, factor)
        # elif self._zoom == 0:
        #     self.fitInView()
        # else:
        #     self._zoom = 0

class DiagramScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(DiagramScene, self).__init__(parent)
        self.drawBG()
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

    def drawBG(self):
        brush = QBrush(QColor('#FFFFFF'))
        # brush.setStyle(Qt.CrossPattern)
        self.setBackgroundBrush(brush)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    app.exec_()

    # def test(self):
    #     ld_fulletch = {'layer': 91, 'datatype': 3}
    #     # ld_partetch = {'layer': 2, 'datatype': 3}
    #     # ld_liftoff  = {'layer': 0, 'datatype': 7}

    #     um        = 1
    #     cm        = 10000*um
    #     wafer_rad = 75*cm
    #     die_size  = [2500*um, 2500*um]
    #     shot_size = [  20,   20]
    #     main_cell = gdspy.Cell('MAIN')
    #     shot_cell = gdspy.Cell('SHOT')
    #     die_cell  = gdspy.Cell('DIE')
    #     die_rect  = gdspy.Rectangle((0, 0), (die_size[0], die_size[1]))

    #     die_cell.add(die_rect)
    #     shot_cell.add(gdspy.CellArray(die_cell,  shot_size[0], shot_size[1], (die_size[0], die_size[1])))
    #     main_cell.add(gdspy.CellArray(shot_cell, 20, 20, (die_size[0]*shot_size[0], die_size[1]*shot_size[1])))

    #     points = [[wafer_rad * math.cos(i/360*math.pi*2), wafer_rad * math.sin(i/360*math.pi*2)] for i in range(-65, 246, 5)]
    #     poly   = gdspy.Polygon(points, **ld_fulletch)
    #     main_cell.add(poly)

    #     gdspy.write_gds('first.gds')

    #     # Optionally, display all cells using the internal viewer.
    #     # gdspy.LayoutViewer()