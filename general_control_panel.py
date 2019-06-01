
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from uiplus import HBox, VBox, PushButtonPlus, StepEditPlus
from prj_control_panel import prj_control
from map_control_panel import map_control

class general_control(QWidget):
    update_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(general_control, self).__init__(parent)
        self.prj_control = prj_control()
        self.map_control = map_control()
        self.shot_control = prj_control()
        self.next_pb = PushButtonPlus("Next >")
        self.prev_pb = PushButtonPlus("<")
        self.prev_pb.setFixedWidth(30)
        self.step_indicator = StepEditPlus()
        self.setAutoFillBackground(True)
        self.control_page = VBox(self.prj_control, self.map_control, self.shot_control, -1).setSpacing(20)
        self.setLayout(VBox(self.control_page, HBox(self.prev_pb, self.next_pb), self.step_indicator ))
        self.step_indicator.setValue(1)
        self.map_control.hide()
        self.shot_control .hide()
        self.next_pb.clicked.connect(self.next_page)
        self.prev_pb.clicked.connect(self.prev_page)
        self.load_stylesheet()
        self.resize(450, 800)
        self.setFixedWidth(400)
        self._current_page_index = 0
        self._page_count  = 3

    def next_page(self):
        if self._current_page_index < self._page_count-1:
            self._current_page_index +=1
            self.show_page(self._current_page_index)
            self.step_indicator.setValue(self._current_page_index+1)

    def prev_page(self):
        if self._current_page_index > 0:
            self._current_page_index -=1
            self.show_page(self._current_page_index)
            self.step_indicator.setValue(self._current_page_index+1)
        
    def show_page(self, page_index):
        for i in range(self._page_count):
            page_item = self.control_page.itemAt(i).widget()
            if page_item.isVisible():
                page_item.hide()
        self.control_page.itemAt(page_index).widget().show()
        
        
        self.step_indicator.setValue(1)

    def load_stylesheet(self):
        f = QFile("./style.qss")
        if not f.exists():
            return ""
        else:
            f.open(QFile.ReadOnly | QFile.Text)
            ts = QTextStream(f)
            stylesheet = ts.readAll()
            self.setStyleSheet(stylesheet)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = general_control()
    MainWindow.show()
    app.exec_()

