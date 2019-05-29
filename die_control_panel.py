
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from uiplus import HBox, VBox, LineEditPlus, StepEditPlus



class die_control(QWidget):

    def __init__(self, parent=None):
        super(die_control, self).__init__(parent)
        
        self.setAutoFillBackground(True)
        self.l1 = LineEditPlus(prefix = "Die  size",  postfix = "um²",  mode = LineEditPlus.dual_text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.l2 = LineEditPlus(prefix = "Shot Size",  postfix = "die²", mode = LineEditPlus.dual_text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.l1.setText("1250", target = LineEditPlus.text_edit).setText("1550", target = LineEditPlus.dual_text_edit)
        self.l1.setPrefixWidth(100)
        self.l1.setPostfixWidth(65)
        self.l1.setPlaceholderText("Width",  target = LineEditPlus.text_edit)
        self.l1.setPlaceholderText("Height", target = LineEditPlus.dual_text_edit)
        self.l1.setAlignment(Qt.AlignCenter, LineEditPlus.text_edit | LineEditPlus.dual_text_edit)
        self.l1.setText("x", target = LineEditPlus.seperate_1st_label)
        v = QDoubleValidator(1, 15000, 2)
        v.setNotation(QDoubleValidator.StandardNotation)
        self.l1.setValidator(v, target = LineEditPlus.text_edit | LineEditPlus.dual_text_edit)

        self.l2.setText("12", target = LineEditPlus.text_edit).setText("9", target = LineEditPlus.dual_text_edit)
        self.l2.setPrefixWidth(100)
        self.l2.setPostfixWidth(65)
        self.l2.setAlignment(Qt.AlignCenter, LineEditPlus.text_edit | LineEditPlus.dual_text_edit)
        self.l2.setPlaceholderText("Row",   target = LineEditPlus.text_edit)
        self.l2.setPlaceholderText("Column", target = LineEditPlus.dual_text_edit)
        self.l2.setText("x", target = LineEditPlus.seperate_1st_label)        
        self.l2.setValidator(QIntValidator(1, 100),     target = LineEditPlus.text_edit | LineEditPlus.dual_text_edit)

        self.setLayout(VBox(self.l1, self.l2, StepEditPlus()))
        self.load_stylesheet()

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
if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = die_control()
    MainWindow.show()
    app.exec_()

