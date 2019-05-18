
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *




class map_control(QWidget):
    def __init__(self, parent=None):
        super(map_control, self).__init__(parent)
        
        # self._die_width_edit  = QLineEdit()
        # self._die_htight_edit = QLineEdit()
        # self._shot_column_edit = QLineEdit()
        # self._shot_row_edit = QLineEdit()
        # self._map_offset_x_edit = QLineEdit()
        # self._map_offset_y_edit = QLineEdit()
        # self._ebr_edit = QLineEdit()
        h = QVBoxLayout()
        k = PushButtonPlus("update")
        l = LineEditPlus()
        m = HorizontalLinePlus()

        h.addWidget(m)
        h.addWidget(l)
        h.addWidget(k)
        k.clicked.connect(self.load_stylesheet)
        self.setLayout(h)
        self.setStyleSheet("""
            QWidget {
                background-color: "#ffffff";
            }""")

    def load_stylesheet(self):
        f = QFile("./style.qss")
        if not f.exists():
            return ""
        else:
            print("update")
            f.open(QFile.ReadOnly | QFile.Text)
            ts = QTextStream(f)
            stylesheet = ts.readAll()
            self.setStyleSheet(stylesheet)    

class HorizontalLinePlus(QWidget):
    def __init__(self, parent=None):
        super(HorizontalLinePlus, self).__init__(parent)
        self.h = QHBoxLayout()
        f1 = QFrame()
        f2 = QFrame()
        f1.setObjectName("hline")
        f2.setObjectName("hline")
        f1.setFrameStyle(QFrame.HLine | QFrame.Plain)
        f2.setFrameStyle(QFrame.HLine |  QFrame.Plain)
        f1.setLineWidth(1)
        f2.setLineWidth(1)
        f1.setMidLineWidth(1)
        f2.setMidLineWidth(1)        
        f1.setFixedWidth(20)
        L1 = QLabel("Label")
        self.h.addWidget(f1)
        self.h.addWidget(L1)
        self.h.addWidget(f2)
        self.setLayout(self.h)
        L1.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))


class PushButtonPlus(QPushButton):
    def __init__(self, parent=None):
        super(PushButtonPlus, self).__init__(parent)

class LineEditPlus(QWidget):
    def __init__(self, mode = "", parent=None):
        super(LineEditPlus, self).__init__(parent)
        self._prefix_label   = QLabel("prefix")
        self._postfix_label  = QLabel("um")
        self._postfix_button = QPushButton()
        self._postfix_combo  = QComboBox()
        self._line_edit      = QLineEdit()
        self._layout         = QHBoxLayout()
        
        self._prefix_label.setObjectName("prefix_label")
        self._postfix_label.setObjectName("postfix_label")
        self._postfix_button.setObjectName("posfix_button")
        self._postfix_combo.setObjectName("postfix_combo")
        self._line_edit.setObjectName("line_edit")

        self._line_edit.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

        h = QHBoxLayout()
        h.setSpacing(0)
        h.setContentsMargins(QMargins(0,0,0,0))
        h.addWidget(self._prefix_label)
        h.addWidget(self._line_edit)
        h.addWidget(self._postfix_label)
        self.setLayout(h)


    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = map_control()
    MainWindow.show()
    app.exec_()

