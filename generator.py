
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtOpenGL import *
import gdspy
import math
import importlib.util

um           = 1
mm           = 1000*um
wafer_rad    = 76.2*mm
ebr          = 3*mm
flat_exclude = 10*mm

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
        row    = 5
        column = 5
        die_w  = 2700*um
        die_h  = 2700*um
        step_x = die_w*column
        step_y = die_h*row
        offset_x = -die_w*2.5*um
        offset_y = -750*um
        for r in range(-8, 8):
            for c in range(-8, 8):
                self.scene.addItem(shot_item(offset_x + (step_x*c), offset_y + (step_y*r), row, column, die_w, die_h, self.scene))
        
        self.scene.addItem(origin_item(offset_x, offset_y))
        self.scene.addItem(asml_ak_item(-45*mm, 0))
        self.scene.addItem(asml_ak_item( 45*mm, 0))
        self.scene.addItem(wafer_item())
        self.scene.addItem(ebr_item(ebr= ebr, flat_exclude= flat_exclude))
        




class shot_item(QGraphicsItem):
    def __init__(self, x, y, row, column, die_width, die_height, scene, parent=None):
        super(shot_item, self).__init__(parent)
        self._scene      = scene
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

    def append_dies(self):
        die_pen         = QPen(QColor('#dadada'), 1, Qt.SolidLine)
        die_pen.setCosmetic(True)
        dummy_die_brush = QBrush(Qt.NoBrush)
        gross_die_brush = QBrush(QColor('#777777'), Qt.SolidPattern)

        for column in range(self._column):
            for row in range(self._row):
                x, y, w, h = self._x + (column * self._die_width), self._y +( row * self._die_height), self._die_width, self._die_height
                self._scene.addItem(die_item(x, y, w, h, dummy_die_brush, gross_die_brush, die_pen))
    
    def draw_dies(self, painter):
        for column in range(self._column):
            for row in range(self._row):
                x, y, w, h = self._x + (column * self._die_width), self._y +( row * self._die_height), self._die_width, self._die_height
                rect = QRectF(x, y, w, h)
                painter.setPen( self._die_pen)
                painter.setBrush( self._gross_die_brush if self.validation(rect) else self._dummy_die_brush)
                painter.drawRect(rect)

    def validation(self, rect):
        x = rect.x()
        y = rect.y()
        w = rect.width()
        h = rect.height()
        return(((x**2) + (y**2))**(0.5) <= wafer_rad-ebr) and (y >= (- wafer_rad + flat_exclude))



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
    def __init__(self, radius = wafer_rad, parent=None):
        super(wafer_item, self).__init__(parent)
        self._x = -radius
        self._y = -radius
        self._w = radius *2
        self._h = radius *2
        
        # self._points = [QPointF(radius * math.cos(i/360*math.pi*2), radius * math.sin(i/360*math.pi*2)) for i in range(-90+8.838, 270+8.838, 5)]
        self._pen   = QPen(QColor('#444444'), .5, Qt.SolidLine)
        self._pen.setCosmetic(True)
        self._brush = QBrush(Qt.NoBrush)    

    def paint(self, painter, option, widget):
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        # painter.drawPolygon(QPolygonF(self._points))
        k=20
        painter.drawArc(self.boundingRect(), (90-k)*16, (-360+2*k)*16)
        # painter.drawLine(self.boundingRect(), (90-k)*16, (-360+2*k)*16)

    def boundingRect(self):
        return QRectF(self._x, self._y, self._w, self._h)

class ebr_item(wafer_item):
    def __init__(self, ebr, flat_exclude, parent=None):
        super(ebr_item, self).__init__(radius = (wafer_rad - ebr), parent = parent)  


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


    # def fitInView(self, scale=True):

    #     if True:
    #         self.setSceneRect(rect)
    #         if self.hasPhoto():
    #             unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
    #             self.scale(1 / unity.width(), 1 / unity.height())
    #             viewrect = self.viewport().rect()
    #             scenerect = self.transform().mapRect(rect)
    #             factor = min(viewrect.width() / scenerect.width(),
    #                          viewrect.height() / scenerect.height())
    #             self.scale(factor, factor)
    #         self._zoom = 0

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