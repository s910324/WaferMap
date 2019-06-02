
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from general_control_panel import general_control
import gdspy
import math
import importlib.util
from uiplus import HBox
um           = 1
mm           = 1000*um
wafer_rad    = 75.0*mm
ebr          = 2*mm
flat_exclude = 7*mm
flat_dist           = 69.27*mm
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.shot_view    = DiagramView()
        self.wafer_view   = DiagramView()
        self.shot_scene   = GraphicScene(self.shot_view)
        self.wafer_scene  = GraphicScene(self.wafer_view)
        self.control      = general_control()
        self.control_dock = QDockWidget()
        
        self.control_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.control_dock.setWidget(self.control)
        self.control_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.control_dock.setTitleBarWidget(QWidget())
        self.addDockWidget(Qt.LeftDockWidgetArea, self.control_dock)
        self.shot_scene.setSceneRect(-1500*um, -1500*um, 3000*um, 3000*um)
        self.wafer_scene.setSceneRect(-wafer_rad, -wafer_rad, 2*wafer_rad, 2*wafer_rad)

        self.control.next_pb.clicked.connect(self.m)
        self.control.prev_pb.clicked.connect(self.n)
        self.shot_view.setScene(self.shot_scene)
        self.wafer_view.setScene(self.wafer_scene)
        w = QWidget()
        w.setLayout(HBox(self.shot_view, self.wafer_view))
        self.setCentralWidget(w)
        self.shot_view.show()
        self.wafer_view.hide()
       
        self.wafer = None
        
        self.n()
        self.shot_view.centerOn (0,0)
        self.shot_view.setRenderHints (QPainter.HighQualityAntialiasing | QPainter.SmoothPixmapTransform)
        self.wafer_view.centerOn (0,0)
        self.wafer_view.setRenderHints (QPainter.HighQualityAntialiasing | QPainter.SmoothPixmapTransform)

        self.setWindowTitle("Fake Wafer Map")
        self.resize(1250, 700)
    
    def n(self):
        factor       = 0.05
        x            = 0
        y            = 0
        row_count    = 10
        column_count = 15
        die_width    = 500*um
        die_height   = 800*um
        self.wafer_view.hide()
        self.shot_view.show()
        shot         = shot_item(-(column_count*die_width)/2, -(row_count*die_height)/2, row_count, column_count, die_width, die_height, 0, 0, None)
        gshot        = shot_graphic_item(shot)
        self.shot_view.scale(1*factor, -1*factor)
        self.shot_scene.addItem(gshot)

    def m(self):
        factor       = 0.003
        row    = 12
        column = 12
        die_w  = 1500*um
        die_h  = 1500*um
        step_x = die_w*column
        step_y = die_h*row
        offset_x = -step_x/2
        offset_y = -750*um
        
        self.shot_view.hide()
        self.wafer_view.show()
        # offset_y = 0*um
        self.wafer_view.scale(1*factor, -1*factor)
        self.wafer = wafer_graphic_item(wafer_rad)
        # self.control.w.clicked.connect(lambda : self.wafer.shift_all_shots(     0,  100*um))
        # self.control.s.clicked.connect(lambda : self.wafer.shift_all_shots(     0, -100*um))
        # self.control.a.clicked.connect(lambda : self.wafer.shift_all_shots(-100*um,      0))
        # self.control.d.clicked.connect(lambda : self.wafer.shift_all_shots( 100*um,      0))
        # self.control.k.clicked.connect(lambda : self.refresh())
        self.wafer.add_zero_mk(-45*mm, 0).add_zero_mk(45*mm, 0).add_indicator_mk(offset_x, offset_y)

        self.wafer.populate_shots( die_w, die_h, row, column, offset_x, offset_y)
        self.wafer_scene.addItem(self.wafer)
        self.wafer.print_info()

    def refresh(self):
        w, h = self.control.get_die_size()
        r, c = self.control.get_shot_size()
        self.wafer.populate_shots(w, h, r, c, 0, 0)


class die_item(object):
    gross_die    = 0X10000
    pcm_die      = 0X01000
    dummy_die    = 0x00100
    selected_die = 0x00010
    disabled_die = 0x00001
    def __init__(self, x, y, w, h, column_index, row_index, status, shot):
        super(die_item, self).__init__()
        self._shot              = shot
        self._x                 = x
        self._y                 = y
        self._w                 = w
        self._h                 = h
        self._row_index         = row_index
        self._column_index      = column_index
        self._statue            = status

    def die_status(self):
        return self._statue

    def set_die_status(self, status):
        self._statue = status
        return self

    def shift(self, dx, dy):
        self._x += dx
        self._y += dy
        return self


    def boundingRect(self):
        return QRectF(self._x, self._y, self._w, self._h)

class shot_item(object):
    partial_shot  = 0X10
    complete_shot = 0X01
    null_shot     = 0x00
    def __init__(self, x, y, row_count, column_count, die_width, die_height, column_index, row_index, wafer):
        super(shot_item, self).__init__()
        self._wafer              = wafer
        self._row_count          = row_count
        self._column_count       = column_count
        self._row_index          = row_index
        self._column_index       = column_index
        self._die_width          = die_width
        self._die_height         = die_height
        self._x                  = x
        self._y                  = y
        self._w                  = self._die_width  * self._column_count
        self._h                  = self._die_height * self._row_count
        self._die_array          = []
        self._pcm_die_index      = [[0, 0]]
        self._disabled_die_index = []
        self.update_die_array()
                  
    def shot_status(self):
        if self.gross_die_count() > 0 and self.dummy_die_count() == 0:
            return shot_item.complete_shot
        elif self.gross_die_count == 0:
            return shot_item.null_shot
        else:
            return shot_item.partial_shot

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
        self._die_array = []
        for column in range(self._column_count):
            for row in range(self._row_count):
                x, y, w, h = self._x + (column * self._die_width), self._y +( row * self._die_height), self._die_width, self._die_height
                die = die_item(x, y, w, h, column_index=column, row_index=row, status = die_item.disabled_die, shot=self)
                if self._wafer and self._wafer.in_ebr_range(die.boundingRect()) == wafer_graphic_item.fully_in_range:

                    if   [row, column] in self._pcm_die_index:
                        die.set_die_status(die_item.pcm_die)

                    elif [row, column] in self._disabled_die_index:
                        die.set_die_status(die_item.disabled_die)

                    else:
                        die.set_die_status(die_item.gross_die)

                else:
                    die.set_die_status(die_item.dummy_die)
                self._die_array.append(die)

    def die_ststus_count(self, status):
        return sum([ die.die_status() == status for die in self._die_array])

    def gross_die_count(self):
        return self.die_ststus_count(die_item.gross_die)

    def dummy_die_count(self):
        return self.die_ststus_count(die_item.dummy_die)

    def pcm_die_count(self):
        return self.die_ststus_count(die_item.pcm_die)

    def disabled_die_count(self):
        return self.die_ststus_count(die_item.disabled_die)

    def boundingRect(self):
        return QRectF(self._x, self._y, self._w, self._h)




class shot_graphic_item(QGraphicsItem):
    def __init__(self, shot,  parent=None):
        super(shot_graphic_item, self).__init__(parent)
        self._shot_item       = shot
        self._annotation_lines = []
        self._annotation_offset = 800*um

        self._shot_pen        = QPen(QColor('#444444'), 1, Qt.SolidLine)
        self._shot_brush      = QBrush(Qt.NoBrush)
        self._die_pen         = QPen(QColor('#dadada'), 1, Qt.SolidLine)
        self._gross_die_brush = QBrush(QColor('#777777'), Qt.SolidPattern)
        self._arrow_brush      = QBrush(QColor('#444444'), Qt.SolidPattern)
        self._pcm_die_brush   = QBrush(QColor('#7CC292'), Qt.SolidPattern)
        self._shot_pen.setCosmetic(True)
        self._die_pen.setCosmetic(True)
        self.init_die()
        self.init_annotation()

    def init_die(self):
        for die in self._shot_item._die_array:
            die.set_die_status(die_item.gross_die)

    def init_annotation(self):
        item             = self._shot_item.boundingRect()
        offset           = self._annotation_offset
        # shot_width_anno  = QLineF(QPointF(                        item.x(), item.y() - offset), QPointF(        item.x()+item.width(),         item.y() - offset))
        # shot_height_anno = QLineF(QPointF(item.x() + item.width() + offset,          item.y()), QPointF(item.x()+item.width()+ offset,  item.y() + item.height()))
        # shot_width_anno  = QLineF(QPointF(               item.x(), item.y()), QPointF(item.x() + item.width(),                  item.y()))
        shot_width_anno  = QLineF(QPointF(item.x() + item.width(), item.y() +  item.height()), QPointF(               item.x(),  item.y() + item.height()))
        shot_height_anno = QLineF(QPointF(item.x() + item.width(),                  item.y()), QPointF(item.x() + item.width(),  item.y() + item.height()))
        self._annotation_lines.append(shot_width_anno)
        self._annotation_lines.append(shot_height_anno)
 
    def paint(self, painter, option, widget):

        for die in self._shot_item._die_array:


            if die.die_status() & die_item.gross_die  == die_item.gross_die:
                painter.setBrush(self._gross_die_brush)
            if die.die_status() & die_item.pcm_die    == die_item.pcm_die:
                painter.setBrush(self._pcm_die_brush)   
            painter.setPen( self._die_pen)
            painter.drawRect(die.boundingRect())
            if die.die_status() & die_item.pcm_die    == die_item.pcm_die:
                rect = die.boundingRect()
                pen=QPen(QColor('#ffffff'), 1, Qt.SolidLine)
                painter.setPen( pen) 
                painter.setFont(QFont("Lato", 150))  
                painter.save()
                painter.scale(1, -1)
                painter.drawText(QRectF(rect.x(), -rect.height()-rect.y(), rect.width(), rect.height()), Qt.AlignCenter ,"PCM")
                painter.restore()

            painter.setPen(self._shot_pen)
            painter.setBrush(self._shot_brush)
            painter.drawRect(self._shot_item.boundingRect())
            painter.setBrush(self._arrow_brush)
            painter.setFont(QFont("Lato", 150))
        for anno_line in self._annotation_lines:
            anno_line, head_indi_line, tail_indi_line, head_arrow, tail_poly, text_point, txt = self.get_annotation_item(anno_line)
            painter.drawLine(anno_line)
            painter.drawLine(head_indi_line)
            painter.drawLine(tail_indi_line)
            painter.drawPolygon(head_arrow)
            painter.drawPolygon(tail_poly)
            painter.save()
            painter.scale(1, -1)

            painter.drawText(QPointF(text_point.x()-500*um, -text_point.y()),txt)
            painter.restore()


    def get_annotation_item(self, line, offset = 300*um, arrow_size = 120*um, text_offset = 200*um):
        angle  = math.pi * 2.0 - math.acos(line.dx() / line.length()) if line.dy() >= 0 else math.acos(line.dx() / line.length())
        nangle = angle - math.pi
        length = line.length()

        tgt_line = QLineF(line.p1(), line.p2())

        line = self.true_translate(line,  -offset * math.sin(angle), -offset * math.cos(angle))
        anno_line  = QLineF(line.p1(), line.p2())
        anno_p1 = anno_line.p1()
        anno_p2 = anno_line.p2()

        sourceArrowP1 =  anno_p1 + QPointF(math.sin(  angle           + math.pi / 3) * arrow_size, math.cos(  angle           + math.pi / 3) * arrow_size )
        sourceArrowP2 =  anno_p1 + QPointF(math.sin(  angle + math.pi - math.pi / 3) * arrow_size, math.cos(  angle + math.pi - math.pi / 3) * arrow_size )
        tailpoint1    = (anno_p1 + (sourceArrowP1 + sourceArrowP2)/2)/2

        drainArrowP1  =  anno_p2 + QPointF(math.sin( nangle           + math.pi / 3) * arrow_size, math.cos( nangle           + math.pi / 3) * arrow_size )
        drainArrowP2  =  anno_p2 + QPointF(math.sin( nangle + math.pi - math.pi / 3) * arrow_size, math.cos( nangle + math.pi - math.pi / 3) * arrow_size )
        tailpoint2    = (anno_p2 + (drainArrowP1 + drainArrowP2)/2)/2

        head_arrow_polygon = QPolygonF([anno_p1, sourceArrowP1,tailpoint1, sourceArrowP2])
        tail_arrow_polygon = QPolygonF([anno_p2,  drainArrowP1,tailpoint2,  drainArrowP2])
        
        line = self.true_translate(line, -arrow_size * math.sin(angle), -arrow_size * math.cos( angle))
        indicater_line  = QLineF(line.p1(), line.p2())
        head_indicater_line = QLineF(line.p1(), tgt_line.p1())
        tail_indicator_line = QLineF(line.p2(), tgt_line.p2())

        line = self.true_translate(line, -text_offset * math.sin(angle), -text_offset * math.cos( angle))
        text_line  = QLineF(line.p1(), line.p2())
        text_point  = QPointF( ( text_line.p1().x() + text_line.p2().x()) /2 - math.sin(angle)* 400*um,  ( text_line.p1().y() + text_line.p2().y()) /2)


        return anno_line, head_indicater_line, tail_indicator_line, head_arrow_polygon, tail_arrow_polygon, text_point, "%.2fum" % length

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSceneHasChanged:
            if self.scene():
                self.scene().clicked.connect(self.select_die)
        return QGraphicsItem.itemChange(self, change, value)

    def select_die(self, button, pos):
        if button == Qt.LeftButton:
            if self.boundingRect().contains(pos):
                for die in self._shot_item._die_array:
                    if die.boundingRect().contains(pos):
                        die.set_die_status(die.die_status() ^ die_item.pcm_die)
                        self.scene().update(self.boundingRect())
                        return

    def true_translate(self, line, dx, dy):
        p1 = QPointF((line.p1().x() + dx), (line.p1().y() + dy) )
        p2 = QPointF((line.p2().x() + dx), (line.p2().y() + dy) )
        return QLineF(p1, p2)

    def boundingRect(self):
        return self._shot_item.boundingRect()

class wafer_graphic_item(QGraphicsItem):
    fully_in_range    = 0x11
    partilly_in_range = 0x10
    not_in_range      = 0x00
    def __init__(self, radius = wafer_rad, parent=None):
        super(wafer_graphic_item, self).__init__(parent)
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
        self._selected_shot       = []
        self._indicator_mk        = []
        self._wafer_pts           = []
        self._ebr_pts             = []




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

    def print_info(self):
        print (
            """complete shots: %d;\npartial shots:  %d;\ngross die:      %d;\n""" % (self.complete_shot_count(), self.partial_shot_count(), self.gross_die_count()))  

    def populate_shots(self, die_w, die_h, row_count, column_count, offset_x, offset_y):
        rect = QRectF()
        self.clearShots()
        self._indicator_mk = []
        self.add_indicator_mk(offset_x, offset_y)
        step_x              = die_w*column_count
        step_y              = die_h*row_count
        self._die_w         = die_w
        self._die_h         = die_h
        self._shot_row      = row_count
        self._shot_column   = column_count
        self._shot_offset_x = offset_x
        self._shot_offset_y = offset_y
        for c in range(math.ceil((self._radius-self._ebr_width-offset_x)/step_x) * -1, math.ceil((self._radius-self._ebr_width+offset_x)/step_x)+1):                
            for r in range(math.ceil((self._radius-flat_exclude)/step_y) * -1, math.ceil((self._radius-self._ebr_width)/step_y)+1):  
                shot = shot_item(offset_x + (step_x*c), offset_y + (step_y*r), row_count, column_count, die_w, die_h, row_index = r, column_index = c, wafer = self)  

                if not self.in_ebr_range(shot.boundingRect()) == wafer_graphic_item.not_in_range and shot.gross_die_count()>=10:
                    self.addShot(shot)
                    rect.united(shot.boundingRect())

        if self.scene():
            self.scene().update(rect)


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
                if not self.in_ebr_range(shot.boundingRect()) == wafer_graphic_item.not_in_range: 
                    if self.in_zero_range(shot.boundingRect()) == wafer_graphic_item.fully_in_range: 
                        lc = (self.collision_avoid(QRect(-45*mm-750*um, -750*um, 1500*um, 1500*um), shot.boundingRect()))
                        rc = (self.collision_avoid(QRect( 45*mm-750*um, -750*um, 1500*um, 1500*um), shot.boundingRect()))
                        print ("d", lc, rc)
                        kd = math.ceil((lc[1] + rc[1])/ die_h)
                    shot.shift_by_die(0, kd)
                    if not self.in_ebr_range(shot.boundingRect()) == wafer_graphic_item.not_in_range and shot.gross_die_count()>=1:
                        self.addShot(shot)

            for ru in range(0, math.ceil((self._radius-self._ebr_width)/step_y)+1):
                shot = shot_item(offset_x + (step_x*c), offset_y + (step_y*ru), row, column, die_w, die_h, self)
                if  not self.in_ebr_range(shot.boundingRect()) == wafer_graphic_item.not_in_range: 
                    if self.in_zero_range(shot.boundingRect()) == wafer_graphic_item.fully_in_range: 
                        lc = (self.collision_avoid(QRect(-45*mm-750*um, -750*um, 1500*um, 1500*um), shot.boundingRect()))
                        rc = (self.collision_avoid(QRect( 45*mm-750*um, -750*um, 1500*um, 1500*um), shot.boundingRect()))
                        print ("u", lc, rc)
                        ku = math.ceil((lc[1] + rc[1])/ die_h)
                    shot.shift_by_die(0, ku)
                    if not self.in_ebr_range(shot.boundingRect()) == wafer_graphic_item.not_in_range and shot.gross_die_count()>=1:
                        self.addShot(shot)        




    def shift_all_shots(self, dx, dy):
        self.populate_shots( self._die_w, self._die_h, self._shot_row, self._shot_column, self._shot_offset_x + dx, self._shot_offset_y + dy)
        # for i in range(len(self._indicator_mk)):
        #     self._indicator_mk[i] = self._indicator_mk[i].translate(dx, dy)

        br         = self.boundingRect()
        shot_w     = self._shot_column * self._die_w
        shot_h     = self._shot_row    * self._die_h
        x, y, w, h = br.x()-shot_w, br.y()-shot_h, br.width() + shot_w*2, br.height() + shot_h*2
        self.scene().update(QRectF(x, y, w, h))
        self.print_info()
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

            for shot in self._shot_array:
                if shot.boundingRect().contains(pos):
                    for die in shot._die_array:
                        if die.boundingRect().contains(pos):
                            die.set_die_status(die.die_status() ^ die_item.disabled_die)
                            self.scene().update(shot.boundingRect())
                            return

    def add_wafer_pts(self):
        self._wafer_pts = []
        self._ebr_pts   = []  
        points          = 80
        delta_theta1    = ((2 * math.pi) - (2 * self._flat_theta))/points
        delta_theta2    = ((2 * math.pi) - (2 * self._exclude_theta))/points
      
        for  i in range(points+1):
            theta = 1.5 * math.pi + self._flat_theta + delta_theta1 * i
            self._wafer_pts.append(QPointF(self._radius * math.cos(theta), self._radius * math.sin(theta)))
            theta = 1.5 * math.pi + self._exclude_theta + delta_theta2 * i
            self._ebr_pts.append(QPointF((self._radius-self._ebr_width) * math.cos(theta), (self._radius-self._ebr_width) * math.sin(theta)))
            


    def gross_die_count(self):
        return sum([ shot.gross_die_count() for shot in self._shot_array])

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


        for shot in self._shot_array:
            for die in shot._die_array:
                painter.setPen( self._die_pen)
                if die.die_status() & die_item.gross_die    == die_item.gross_die:
                    painter.setBrush(self._gross_die_brush)
                if die.die_status() & die_item.dummy_die    == die_item.dummy_die:
                    painter.setBrush(self._dummy_die_brush)
                if die.die_status() & die_item.pcm_die == die_item.pcm_die:
                    painter.setBrush(self._dummy_die_brush)                    
                if die.die_status() & die_item.disabled_die == die_item.disabled_die:
                    painter.setBrush(self._selected_die_brush)                    

                painter.drawRect(die.boundingRect())

            painter.setPen(self._shot_pen)
            painter.setBrush(self._shot_brush)
            painter.drawRect(shot.boundingRect())


        painter.setPen(self._wafer_pen)
        painter.setBrush(self._wafer_brush)
        painter.drawPolygon(QPolygonF(self._wafer_pts))
        painter.drawPolygon(QPolygonF(self._ebr_pts))


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
            return wafer_graphic_item.fully_in_range
        elif any(detection):
            return wafer_graphic_item.partilly_in_range
        else:
            return wafer_graphic_item.not_in_range

        return wafer_graphic_item.fully_in_range if self._ebr_polygon.intersected(rect) else wafer_graphic_item.not_in_range

    def in_zero_range(self, rect):
        ''''must add marks first before adding shots'''
        return wafer_graphic_item.fully_in_range if any([mk_rect.intersected(rect) for mk_rect in self._zero_mk]) else wafer_graphic_item.not_in_range

    def collision_avoid(self, main_rect, comp_rect):
        line = QLineF(main_rect.center(), comp_rect.center())
        dx = 0 if abs(line.dx()) >= (main_rect.width()  + comp_rect.width())/2  else (main_rect.width()  + (comp_rect.width())/2  - abs(line.dx())) * math.copysign(1, line.dx())
        dy = 0 if abs(line.dy()) >= (main_rect.height() + comp_rect.height())/2 else (main_rect.height() + (comp_rect.height())/2 - abs(line.dy())) * math.copysign(1, line.dy())
        return [dx, dy] if (not dx == 0) and not(dy == 0) else [0, 0]


    def addShot(self, shot):
        self._shot_array.append(shot)
     

    def clearShots(self):
        self._shot_array = []
        self.clearSelection()

    def clearSelection(self):
        self._selected_shot = []


    def test(self):
        pass
        # ld_fulletch = {'layer': 91, 'datatype': 1}
        # ld_partetch = {'layer': 2, 'datatype': 3}
        # ld_liftoff  = {'layer': 0, 'datatype': 7}

        # # um        = 1
        # # cm        = 10000*um
        # # wafer_rad = 75*cm
        # # die_size  = [2500*um, 2500*um]
        # # shot_size = [  20,   20]
        # main_cell = gdspy.Cell('MAIN')
        # # shot_cell = gdspy.Cell('SHOT')
        # die_cell  = gdspy.Cell('DIE')
        # # main_cell.add(die_cell)

        # for die in self._gross_die:
        #     die_rect  = gdspy.Rectangle(((die.x()), (die.y())), ( (die.x()+die.width()), (die.y()+die.height())), **ld_liftoff)
        #     die_cell.add(die_rect)
        

        
        # # shot_cell.add(gdspy.CellArray(die_cell,  shot_size[0], shot_size[1], (die_size[0], die_size[1])))
        # # main_cell.add(gdspy.CellArray(shot_cell, 20, 20, (die_size[0]*shot_size[0], die_size[1]*shot_size[1])))

        # wafer_poly = gdspy.Polygon([((qp.x()), (qp.y()))for qp in self._wafer_pts], **ld_fulletch)
        # ebr_poly   = gdspy.Polygon([(qp.x(), qp.y())for qp in self._ebr_pts],   **ld_partetch)
        # main_cell.add(wafer_poly)
        # main_cell.add(ebr_poly)
        # gdspy.write_gds('first.gds')





class DiagramView(QGraphicsView):
    def __init__(self, parent=None):
        super(DiagramView, self).__init__(parent)        
        self.init_ui()
        self._drag_enabled = False
        self._zoom         = 1
        self._drag_pos     = None
        self._x            = 0
        self._y            = 0

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

    def mouseMoveEvent(self, event):

        if self._drag_enabled:
            
            delta = self.mapToScene(event.pos()) - self.mapToScene(self._drag_pos)
            self.PanView(delta)
            self._drag_pos = event.pos()
        QGraphicsView.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._drag_enabled = True
            self._drag_pos =event.pos()
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._drag_enabled = False
        QGraphicsView.mouseReleaseEvent(self, event)

    def PanView(self, delta):
        viewCenter = QPoint((self.viewport().width() / 2) - delta.x()/100, (self.viewport().height() / 2) + delta.y()/100)
        newCenter = self.mapToScene(viewCenter)
        self.centerOn(newCenter)

class GraphicScene(QGraphicsScene):
    clicked = pyqtSignal(Qt.MouseButton, QPointF)
    keyed   = pyqtSignal(str)
    def __init__(self, parent=None):
        super(GraphicScene, self).__init__(parent) 

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
        self.clicked.emit(event.button(), event.scenePos())
        if event.button() == Qt.LeftButton:
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

