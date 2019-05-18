import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *

class BoxLayout(QBoxLayout):
	def __init__(self, direction, ui_list):
		super().__init__(direction)

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


class HBox(BoxLayout):
	def __init__(self, *ui_list):
		super().__init__(QBoxLayout.LeftToRight, ui_list)
		

class VBox(BoxLayout):
	def __init__(self, *ui_list):
		super().__init__(QBoxLayout.TopToBottom, ui_list)		
