import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *

class BoxLayout(QBoxLayout):
    def __init__(self, direction, ui_list):
        super().__init__(direction)
        self.setLayoutList(ui_list)

    def setLayoutList(self, ui_list):
        self.clearLayout()
        if ui_list:
            for item in ui_list:
                if isinstance(item, int):
                    if item >= 0:
                        self.addSpacing(item)
                    else:
                        self.addStretch()
                elif issubclass(type(item), QWidget):
                    self.addWidget(item)
                elif issubclass(type(item), QLayout):
                    self.addLayout(item)
                else:
                    raise TypeError("item %s with object type %s is not supported) " % (item, type(item)))      

    def clearLayout(self):
        for index in range(self.count()):
            item = self.takeAt(index)
            w    = item.widget()
            l    = item.layout()
            if issubclass(type(w), QWidget):
                    w.deleteLater()
            if issubclass(type(l), BoxLayout):
                    l.clearLayout()


class HBox(BoxLayout):
    def __init__(self, *ui_list):
        super().__init__(QBoxLayout.LeftToRight, ui_list)



class VBox(BoxLayout):
    def __init__(self, *ui_list):
        super().__init__(QBoxLayout.TopToBottom, ui_list)       
