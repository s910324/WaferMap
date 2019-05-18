
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from uiplus import HBox, VBox



class map_control(QWidget):
    def __init__(self, parent=None):
        super(map_control, self).__init__(parent)
        

        h = QVBoxLayout()
        k = PushButtonPlus("update")
        l = LineEditPlus()
        m = HorizontalLinePlus("Cell")

        h.addWidget(m)
        m.v.addWidget(l)
        m.v.addWidget(k)
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
    def __init__(self, text = "Title",  parent=None):
        super(HorizontalLinePlus, self).__init__(parent)
        self.title_label = QLabel(text)
        self.frame_1     = QFrame()
        self.frame_2     = QFrame()
        self.h           = HBox(self.frame_1, self.title_label, self.frame_2)
        self.v           = VBox(self.h)
        self.setLayout(self.v)

        self.title_label.setObjectName("title")
        self.frame_1.setObjectName("hline")
        self.frame_2.setObjectName("hline")

        self.frame_1.setFrameStyle(QFrame.HLine | QFrame.Plain)
        self.frame_2.setFrameStyle(QFrame.HLine | QFrame.Plain)

        self.frame_1.setLineWidth(1)
        self.frame_2.setLineWidth(1)

        self.frame_1.setMidLineWidth(1)
        self.frame_2.setMidLineWidth(1)        
        self.frame_1.setFixedWidth(15)
        
        self.title_label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

    def setTitle(self, text):
        self.title_label.setText(title)




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
        self._layout         = HBox(self._prefix_label, self._line_edit, self._postfix_label)
        
        self._prefix_label.setObjectName("prefix_label")
        self._postfix_label.setObjectName("postfix_label")
        self._postfix_button.setObjectName("posfix_button")
        self._postfix_combo.setObjectName("postfix_combo")
        self._line_edit.setObjectName("line_edit")

        self._line_edit.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))


        self._layout.setSpacing(0)
        self._layout.setContentsMargins(QMargins(0,0,0,0))

        self.setLayout(self._layout)

    def setPostFix(self, postfix):
        self._postfix_label.setText(postfix)


    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = map_control()
    MainWindow.show()
    app.exec_()

