
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from uiplus import HBox, VBox



class map_control(QWidget):
    def __init__(self, parent=None):
        super(map_control, self).__init__(parent)
        

        
        m = HorizontalLinePlus("Cell")
        k = PushButtonPlus("update")
        l1 = LineEditPlus(mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        l2 = LineEditPlus(mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        l3 = LineEditPlus(mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        l4 = LineEditPlus(mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        l1.setPrefixText("Die width").setPostfixText("um").setPrefixWidth(95).setPostfixWidth(60)
        l2.setPrefixText("Die height").setPostfixText("um").setPrefixWidth(95).setPostfixWidth(60)
        l3.setPrefixText("Shot column").setPostfixText("Die(s)").setPrefixWidth(95).setPostfixWidth(60)
        l4.setPrefixText("Shot row").setPostfixText("Die(s)").setPrefixWidth(95).setPostfixWidth(60)

        h = VBox(m, l1, l2, l3, l4, k)
        
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

    prefix_label   = 0x10000
    postfix_label  = 0x00100
    text_edit      = 0x01000
    postfix_button = 0x00010
    postfix_combo  = 0x00001
    def __init__(self, mode = text_edit, parent=None):
        super(LineEditPlus, self).__init__(parent)



        self._mode           = mode
        self._prefix_label   = QLabel()
        self._postfix_label  = QLabel()
        self._postfix_button = QPushButton()
        self._postfix_combo  = QComboBox()
        self._line_edit      = QLineEdit()
        self._layout         = HBox()

        self._prefix_label.setObjectName("prefix_label")
        self._postfix_label.setObjectName("postfix_label")
        self._postfix_button.setObjectName("posfix_button")
        self._postfix_combo.setObjectName("postfix_combo")
        self._line_edit.setObjectName("line_edit")

        self._line_edit.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
     
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(QMargins(0,0,0,0))

        self.setMode(mode)
        self.setLayout(self._layout)

    def setMode(self, mode):
        self._mode = mode
        l = []
        if (LineEditPlus.prefix_label & mode == LineEditPlus.prefix_label):
            l.append(self._prefix_label)

        if (LineEditPlus.text_edit & mode == LineEditPlus.text_edit):
            l.append(self._line_edit)

        if (LineEditPlus.postfix_label & mode == LineEditPlus.postfix_label):
            l.append(self._postfix_label)
        elif (LineEditPlus.postfix_button & mode == LineEditPlus.postfix_button):
            l.append(self._postfix_button)
        elif (LineEditPlus.postfix_combo & mode == LineEditPlus.postfix_combo):
            l.append(self._postfix_combo)
        self._layout.setLayoutList(l)

    def setPlaceholderText(self, placeholder):
        self._line_edit.setPlaceholderText(placeholder)
        return self

    def setValidator(self, validator):
        self._line_edit.setValidator(validator)
        return self

    def setPostfixText(self, postfix):
        self._postfix_label.setText(postfix)
        return self

    def setPrefixText(self, prefix):
        self._prefix_label.setText(prefix)
        return self
    
    def setText(self, text):
        self._line_edit.setText(text)
        return self

    def text(self):
        return self._line_edit.text()

    def postfixText(self):
        return self._postfix_label.text()

    def prefixText(self):
        return self._prefix_label.text()

    def setPrefixWidth(self, width):
        self._prefix_label.setFixedWidth(width)
        return self

    def setTextEditWidth(self, width):
        self._line_edit.setFixedWidth(width)
        return self

    def setPostfixWidth(self, width):
        self._postfix_label.setFixedWidth(width)
        self._postfix_button.setFixedWidth(width)
        self._postfix_combo.setFixedWidth(width)
        return self

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = map_control()
    MainWindow.show()
    app.exec_()

