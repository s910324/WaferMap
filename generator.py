
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from map_control import map_control
import gdspy
import math
import importlib.util

um           = 1
mm           = 1000*um
wafer_rad    = 75.0*mm
ebr          = 2*mm
flat_exclude = 7*mm
flat_dist           = 69.27*mm
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        factor            = 0.003

        self.view         = DiagramView()
        self.scene        = WaferScene(self.view)
        self.control      = map_control()
        self.control_dock = QDockWidget()
        self.control.setFixedWidth(350)
        self.control_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.control_dock.setWidget(self.control)
        self.control_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.control_dock.setTitleBarWidget(QWidget())
        self.addDockWidget(Qt.LeftDockWidgetArea, self.control_dock)

        self.scene.setSceneRect(-wafer_rad, -wafer_rad, 2*wafer_rad, 2*wafer_rad)
        self.view.scale(1*factor, -1*factor)

        self.view.setScene(self.scene)
        self.view.show()
        
        self.wafer = None
        self.setCentralWidget(self.view)
        self.m()
        self.view.centerOn (0,0)
    
        self.view.setRenderHints (QPainter.HighQualityAntialiasing | QPainter.SmoothPixmapTransform)
        self.setWindowTitle("Fake Wafer Map")
        self.resize(1250, 700)
        
        

    def m(self):

        row    = 12
        column = 12
        die_w  = 1500*um
        die_h  = 1500*um
        step_x = die_w*column
        step_y = die_h*row
        offset_x = -step_x/2
        offset_y = -750*um
        # offset_y = 0*um
        self.wafer = wafer_item(wafer_rad)
        self.control.w.clicked.connect(lambda : self.wafer.shift_all_shots(     0,  100*um))
        self.control.s.clicked.connect(lambda : self.wafer.shift_all_shots(     0, -100*um))
        self.control.a.clicked.connect(lambda : self.wafer.shift_all_shots(-100*um,      0))
        self.control.d.clicked.connect(lambda : self.wafer.shift_all_shots( 100*um,      0))
        self.wafer.add_zero_mk(-45*mm, 0).add_zero_mk(45*mm, 0).add_indicator_mk(offset_x, offset_y)

        self.wafer.populate_shots( die_w, die_h, row, column, offset_x, offset_y)
        self.scene.addItem(self.wafer)
        # self.scene.addItem(scene_info_bar())


        print (
            """
            complete shots: %d;
            partial shots:  %d;
            gross die:      %d;

            """ % (self.wafer.complete_shot_count(), self.wafer.partial_shot_count(),self. wafer.gross_die_count()))





class shot_item(object):
    partial_shot  = 0X10
    complete_shot = 0X01
    null_shot     = 0x00
    def __init__(self, x, y, row, column, die_width, die_height, wafer, parent=None):
        super(shot_item, self).__init__()
        self._wafer        = wafer
        self._x            = x
        self._y            = y
        self._die_width    = die_width
        self._die_height   = die_height
        self._row          = row
        self._column       = column
        self._w            = self._die_width  * self._column
        self._h            = self._die_height * self._row
        self._gross_die    = []
        self._dummy_die    = []
        self._disabled_die = []

        self.update_die_array()

    def shot_status(self):
        if self.gross_die_count() > 0 and self.dummy_die_count() == 0:
            return shot_item.complete_shot
        elif self.gross_die_count == 0:
            return shot_item.null_shot
        else:
            return shot_item.partial_shot

    def gross_die_count(self):
        return len(self._gross_die)

    def dummy_die_count(self):
        return len(self._dummy_die)

    def shift(self, dx, dy):
        self._x += dx
        self._y += dy
        if not (dx == 0) or not(dy == 0):
            self.update_die_array()
        return self

    def shift_by_die(self, dx, dy):
        return self.shift(dx * self._die_width, dy * self._die_height)
    
    def shift_by_shot(self, dx, dy):
        return self.shift(dx * self._w, dy * self._h)

    def update_die_array(self):
        self._gross_die  = []
        self._dummy_die  = []
        for column in range(self._column):
            for row in range(self._row):
                x, y, w, h = self._x + (column * self._die_width), self._y +( row * self._die_height), self._die_width, self._die_height
                rect = QRectF(x, y, w, h)
                if self._wafer.in_ebr_range(rect) == wafer_item.fully_in_range:
                    self._gross_die.append(rect)
                else:
                    self._dummy_die.append(rect)


    def boundingRect(self):
        return QRectF(self._x, self._y, self._w, self._h)


class scene_info_bar(QGraphicsItem):
    def __init__(self,  parent=None):
        super(scene_info_bar, self).__init__(parent)
        self._x = 0
        self._y = 0
        self._w = 0
        self._h = 35
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)

    def paint(self, painter, option, widget):

        painter.setPen( QPen(QColor(0, 255, 0, 100)))
        painter.setBrush(QBrush(QColor(0, 255, 55, 100)))

        painter.drawRect(self.boundingRect())
        painter.drawRect(QRect(0, 0, 5, 5))



    def boundingRect(self):
        if self.scene():
            self._x = (self.scene().parent().size().width()/2)*-1
            self._y = ((self.scene().parent().size().height()/2) - self._h)
            self._w = self.scene().parent().size().width()
            self._h = self._h
            print(self.scene().parent().size())
            print (self.scene().sceneRect())
        return QRectF(self._x, self._y, self._w, self._h)

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
        self._shot_offset_x       = 0
        self._shot_offset_y       = 0
        self._die_w               = 0
        self._die_h               = 0
        self._step_x              = 0
        self._step_y              = 0
        self._cx                  = self._x + self._w /2
        self._cy                  = self._y + self._h /2
        self._zero_mk             = []
        self._shot_array          = []
        self._gross_die           = []
        self._dummy_die           = []
        self._selected_shot       = []
        self._selected_die        = []
        self._indicator_mk        = []
        self._wafer_pts           = []
        self._ebr_pts             = []
        self._wafer_polygon       = QPolygonF()
        self._ebr_polygon         = QPolygonF()



        self._wafer_pen          = QPen(QColor('#444444'), .5, Qt.SolidLine)
        self._wafer_brush        = QBrush(Qt.NoBrush)    
        self._shot_pen           = QPen(QColor('#444444'), 1, Qt.SolidLine)
        self._shot_brush         = QBrush(Qt.NoBrush)
        self._die_pen            = QPen(QColor('#dadada'), 1, Qt.SolidLine)
        self._dummy_die_brush    = QBrush(Qt.NoBrush)
        self._selected_shot_pen  = QPen(QColor('#ff0000'), 1, Qt.DashLine)
        self._gross_die_brush    = QBrush(QColor('#777777'), Qt.SolidPattern)
        self._zero_pen           = QPen(Qt.NoPen)
        self._zero_brush         = QBrush(QColor("#444444"), Qt.SolidPattern) 
        self._indicator_pen      = QPen(Qt.NoPen)
        self._indicator_brush    = QBrush(QColor("#ff0000"), Qt.SolidPattern)  
        self._selected_die_brush = QBrush(QColor("#ff0000"), Qt.SolidPattern)  
        self._selected_shot_pen.setCosmetic(True) 
        self._shot_pen.setCosmetic(True)
        self._die_pen.setCosmetic(True)        
        self._wafer_pen.setCosmetic(True)
        self.add_wafer_pts()

    def populate_shots(self, die_w, die_h, row, column, offset_x, offset_y):
        self.clearShots()
        self._indicator_mk = []
        self.add_indicator_mk(offset_x, offset_y)
        step_x              = die_w*column
        step_y              = die_h*row
        self._die_w         = die_w
        self._die_h         = die_h
        self._shot_row      = row
        self._shot_column   = column
        self._shot_offset_x = offset_x
        self._shot_offset_y = offset_y
        print(self._shot_offset_x, self._shot_offset_y)
        for c in range(math.ceil((self._radius-self._ebr_width-offset_x)/step_x) * -1, math.ceil((self._radius-self._ebr_width+offset_x)/step_x)+1):                
            for r in range(math.ceil((self._radius-flat_exclude)/step_y) * -1, math.ceil((self._radius-self._ebr_width)/step_y)+1):  
                shot = shot_item(offset_x + (step_x*c), offset_y + (step_y*r), row, column, die_w, die_h, self)  
                if not self.in_ebr_range(shot.boundingRect()) == wafer_item.not_in_range and shot.gross_die_count()>=30:
                    self.addShot(shot)



    def populate_shots_1(self, die_w, die_h, row, column, offset_x, offset_y):
        self.clearShots()
        step_x              = die_w*column
        step_y              = die_h*row
        self._die_w         = die_w
        self._die_h         = die_h
        self._shot_row      = row
        self._shot_column   = column
        self._shot_offset_x = offset_x
        self._shot_offset_y = offset_x


        for c in range(math.ceil((self._radius-self._ebr_width-offset_x)/step_x) * -1, math.ceil((self._radius-self._ebr_width+offset_x)/step_x)+1):
            column_array = []
            nu = 0
            nd = 0
            ku = 0
            kd = 0
            for rd in range(-1, math.ceil((self._radius-flat_exclude)/step_y) * -1, -1):
                shot = shot_item(offset_x + (step_x*c), offset_y + (step_y*rd), row, column, die_w, die_h, self)
                if not self.in_ebr_range(shot.boundingRect()) == wafer_item.not_in_range: 
                    if self.in_zero_range(shot.boundingRect()) == wafer_item.fully_in_range: 
                        lc = (self.collision_avoid(QRect(-45*mm-750*um, -750*um, 1500*um, 1500*um), shot.boundingRect()))
                        rc = (self.collision_avoid(QRect( 45*mm-750*um, -750*um, 1500*um, 1500*um), shot.boundingRect()))
                        print ("d", lc, rc)
                        kd = math.ceil((lc[1] + rc[1])/ die_h)
                    shot.shift_by_die(0, kd)
                    if not self.in_ebr_range(shot.boundingRect()) == wafer_item.not_in_range and shot.gross_die_count()>=1:
                        self.addShot(shot)

            for ru in range(0, math.ceil((self._radius-self._ebr_width)/step_y)+1):
                shot = shot_item(offset_x + (step_x*c), offset_y + (step_y*ru), row, column, die_w, die_h, self)
                if  not self.in_ebr_range(shot.boundingRect()) == wafer_item.not_in_range: 
                    if self.in_zero_range(shot.boundingRect()) == wafer_item.fully_in_range: 
                        lc = (self.collision_avoid(QRect(-45*mm-750*um, -750*um, 1500*um, 1500*um), shot.boundingRect()))
                        rc = (self.collision_avoid(QRect( 45*mm-750*um, -750*um, 1500*um, 1500*um), shot.boundingRect()))
                        print ("u", lc, rc)
                        ku = math.ceil((lc[1] + rc[1])/ die_h)
                    shot.shift_by_die(0, ku)
                    if not self.in_ebr_range(shot.boundingRect()) == wafer_item.not_in_range and shot.gross_die_count()>=1:
                        self.addShot(shot)        

    def shift_all_shots(self, dx, dy):
        print("dx, dy =", dx, dy)
        self.populate_shots( self._die_w, self._die_h, self._shot_row, self._shot_column, self._shot_offset_x + dx, self._shot_offset_y + dy)
        print(self._shot_offset_x, self._shot_offset_y)
        # for i in range(len(self._indicator_mk)):
        #     self._indicator_mk[i] = self._indicator_mk[i].translate(dx, dy)

        br         = self.boundingRect()
        shot_w     = self._shot_column * self._die_w
        shot_h     = self._shot_row    * self._die_h
        x, y, w, h = br.x()-shot_w, br.y()-shot_h, br.width() + shot_w*2, br.height() + shot_h*2
        self.scene().update(QRectF(x, y, w, h))

        return self

    def itemChange(self, change, value):

        if change == QGraphicsItem.ItemSceneHasChanged:
            if self.scene():
                self.scene().clicked.connect(self.select_die)
        return QGraphicsItem.itemChange(self, change, value)

    def select_shot(self, button, pos):
        if button == Qt.LeftButton:
            for shot in self._selected_shot:
                if shot.boundingRect().contains(pos):
                    self._selected_shot.remove(shot)
                    self.scene().update(shot.boundingRect())
                    return

            for shot in self._shot_array:
                if shot.boundingRect().contains(pos) and shot not in self._selected_shot:
                    self._selected_shot.append(shot)
                    self.scene().update(shot.boundingRect())
                    return

    def select_die(self, button, pos):
        if button == Qt.LeftButton:

            for die_rect in self._selected_die:
                if die_rect.contains(pos):
                    self._selected_die.remove(die_rect)
                    self.scene().update(die_rect)
                    return

            for shot in self._shot_array:
                if shot.boundingRect().contains(pos):
                    for die_rect in shot._gross_die:
                        if die_rect.contains(pos):
                            self._selected_die.append(die_rect)
                            self.scene().update(die_rect)
                            return



    def add_wafer_pts(self):
        self._wafer_pts = []
        self._ebr_pts   = []  
        points          = 100
        delta_theta1    = ((2 * math.pi) - (2 * self._flat_theta))/points
        delta_theta2    = ((2 * math.pi) - (2 * self._exclude_theta))/points
      
        for  i in range(points+1):
            theta = 1.5 * math.pi + self._flat_theta + delta_theta1 * i
            # self._wafer_pts.append(QPointF(self._radius * math.cos(theta), self._radius * math.sin(theta)))
            self._wafer_polygon.append(QPointF(self._radius * math.cos(theta), self._radius * math.sin(theta)))
            theta = 1.5 * math.pi + self._exclude_theta + delta_theta2 * i
            # self._ebr_pts.append(QPointF((self._radius-self._ebr_width) * math.cos(theta), (self._radius-self._ebr_width) * math.sin(theta)))
            self._ebr_polygon.append(QPointF((self._radius-self._ebr_width) * math.cos(theta), (self._radius-self._ebr_width) * math.sin(theta)))


    def gross_die_count(self):
        return len(self._gross_die)

    def complete_shot_count(self):
        return sum([ item.shot_status() == shot_item.complete_shot for item in self._shot_array])

    def partial_shot_count(self):
        return sum([ item.shot_status() == shot_item.partial_shot for item in self._shot_array])

    def add_zero_mk(self,  x, y, w = 1400*um, h = 1400*um):
        self._zero_mk.append(QRectF(x - w/2, y - h/2, w, h))
        return self

    def add_indicator_mk(self, x, y, w = 1000*um, h = 1000*um):
        self._indicator_mk.append(QRectF(x - w/2, y - h/2, w, h))
        return self

    def paint(self, painter, option, widget):

        painter.setPen( self._die_pen)
        painter.setBrush( self._gross_die_brush)
        for die_rect in self._gross_die:
            painter.drawRect(die_rect)


        painter.setBrush( self._selected_die_brush)
        for die_rect in self._selected_die:
            painter.drawRect(die_rect)

        painter.setBrush( self._dummy_die_brush)
        for die_rect in self._dummy_die:
            painter.drawRect(die_rect)        

        painter.setPen(self._shot_pen)
        painter.setBrush(self._shot_brush)        
        for shot in self._shot_array:
            painter.drawRect(shot.boundingRect())

        painter.setPen(self._selected_shot_pen)
        for shot in self._selected_shot:
            painter.drawRect(shot.boundingRect())

        painter.setPen(self._wafer_pen)
        painter.setBrush(self._wafer_brush)
        painter.drawPolygon(self._wafer_polygon)
        painter.drawPolygon(self._ebr_polygon)
        # painter.drawPolygon(QPolygonF(self._wafer_pts))
        # painter.drawPolygon(QPolygonF(self._ebr_pts))

        painter.setPen(self._zero_pen)
        painter.setBrush(self._zero_brush)
        for mk_rect in self._zero_mk:
            painter.drawRect(mk_rect)

        painter.setPen(self._indicator_pen)
        painter.setBrush(self._indicator_brush)
        for indicator_rect in self._indicator_mk:
            painter.drawEllipse(indicator_rect)   


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

        return wafer_item.fully_in_range if self._ebr_polygon.intersected(rect) else wafer_item.not_in_range

    def in_zero_range(self, rect):
        ''''must add marks first before adding shots'''
        return wafer_item.fully_in_range if any([mk_rect.intersected(rect) for mk_rect in self._zero_mk]) else wafer_item.not_in_range

    def collision_avoid(self, main_rect, comp_rect):
        line = QLineF(main_rect.center(), comp_rect.center())
        dx = 0 if abs(line.dx()) >= (main_rect.width()  + comp_rect.width())/2  else (main_rect.width()  + (comp_rect.width())/2  - abs(line.dx())) * math.copysign(1, line.dx())
        dy = 0 if abs(line.dy()) >= (main_rect.height() + comp_rect.height())/2 else (main_rect.height() + (comp_rect.height())/2 - abs(line.dy())) * math.copysign(1, line.dy())
        return [dx, dy] if (not dx == 0) and not(dy == 0) else [0, 0]


    def addShot(self, shot):
        self._shot_array.append(shot)
        self._gross_die += shot._gross_die
        self._dummy_die += shot._dummy_die

    def clearShots(self):
        self._shot_array = []
        self._gross_die  = []
        self._dummy_die  = []
        self.clearSelection()

    def clearSelection(self):
        self._selected_shot       = []
        self._selected_die        = []

class DiagramView(QGraphicsView):
    def __init__(self, parent=None):
        super(DiagramView, self).__init__(parent)        
        self.init_ui()
        self._zoom = 1


    def init_ui(self):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setFrameShape(QFrame.NoFrame)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        self.scale(factor, factor)



class WaferScene(QGraphicsScene):
    clicked = pyqtSignal(Qt.MouseButton, QPointF)
    keyed   = pyqtSignal(str)
    def __init__(self, parent=None):
        super(WaferScene, self).__init__(parent) 

        self._parent = parent
        self._key_map = {
                    16777235:"up", 
                    16777237:"down", 
                    16777234:"left", 
                    16777236:"right", 
                    87:"w", 
                    83:"s", 
                    65:"a", 
                    68:"d" 
            }


    def parent(self):
        return self._parent

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.clicked.emit(event.button(), event.scenePos())
            print(event.scenePos())

    def keyPressEvent(self, event):
        if event.key() in self._key_map:
            self.keyed.emit(self._key_map[event.key()])
        print(event.key())

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