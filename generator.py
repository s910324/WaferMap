
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import gdspy
import math
import importlib.util

um        = 1
cm        = 10*um
wafer_dia = 75*cm

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.view  = DiagramView()
        self.scene = DiagramScene()
        self.scene.setSceneRect(0, 0, wafer_dia, wafer_dia)
        self.view.scale(1, -1)
        self.view. scale(0.2, 0.2)
        self.view.setScene(self.scene)
        self.view.show()
        
        v = QVBoxLayout()
        v.addWidget(self.view)
        self.setLayout(v)
        self.m()
        self.view.centerOn (0,0)
        self.showMaximized()
        self.view.setRenderHints (QPainter.HighQualityAntialiasing | QPainter.SmoothPixmapTransform)
        

    def m(self):
        pen = QPen(Qt.white, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        x, y, w, h = 0, 0, 250, 250

        for i in range(20):
            for j in range(20):
                self.scene.addRect (x + (i * w), y + (j * h), w, h, pen)
        points = [QPointF(wafer_dia * math.cos(i/360*math.pi*2), wafer_dia * math.sin(i/360*math.pi*2)) for i in range(-65, 246, 5)]
        self.scene.addPolygon(QPolygonF(points), pen)

    def test(self):
        ld_fulletch = {'layer': 91, 'datatype': 3}
        # ld_partetch = {'layer': 2, 'datatype': 3}
        # ld_liftoff  = {'layer': 0, 'datatype': 7}

        um        = 1
        cm        = 10000*um
        wafer_dia = 75*cm
        die_size  = [2500*um, 2500*um]
        shot_size = [  20,   20]
        main_cell = gdspy.Cell('MAIN')
        shot_cell = gdspy.Cell('SHOT')
        die_cell  = gdspy.Cell('DIE')
        die_rect  = gdspy.Rectangle((0, 0), (die_size[0], die_size[1]))

        die_cell.add(die_rect)
        shot_cell.add(gdspy.CellArray(die_cell,  shot_size[0], shot_size[1], (die_size[0], die_size[1])))
        main_cell.add(gdspy.CellArray(shot_cell, 20, 20, (die_size[0]*shot_size[0], die_size[1]*shot_size[1])))

        points = [[wafer_dia * math.cos(i/360*math.pi*2), wafer_dia * math.sin(i/360*math.pi*2)] for i in range(-65, 246, 5)]
        poly   = gdspy.Polygon(points, **ld_fulletch)
        main_cell.add(poly)

        gdspy.write_gds('first.gds')

        # Optionally, display all cells using the internal viewer.
        # gdspy.LayoutViewer()




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
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
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


    def drawBG(self):
        brush = QBrush(QColor('#fafafa'))
        brush.setStyle(Qt.CrossPattern)
        self.setBackgroundBrush(brush)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    app.exec_()

