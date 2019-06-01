
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from uiplus import HBox, VBox, LineEditPlus, StepEditPlus, PushButtonPlus, HorizontalLinePlus



class prj_control(QWidget):

    def __init__(self, parent=None):
        super(prj_control, self).__init__(parent)
        prefix_w, postfix_w  = 110, 85
        self.setAutoFillBackground(True)
        title = HorizontalLinePlus("Product Information")
        self.proj_info_edit  = LineEditPlus(prefix = "Project ID", postfix = ['6" wafer', '8" wafer'],     mode = LineEditPlus.text_edit      | LineEditPlus.prefix_label | LineEditPlus.postfix_combo)
        self.die_info_edit   = LineEditPlus(prefix = "Die  size",  postfix = "um²",  mode = LineEditPlus.dual_text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.shot_info_edit  = LineEditPlus(prefix = "Shot Size",  postfix = "die²", mode = LineEditPlus.dual_text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)

        
        self.proj_info_edit.setPrefixWidth(prefix_w)
        self.proj_info_edit.setPostfixWidth(postfix_w)
        self.proj_info_edit.setPlaceholderText("Product Name",  target = LineEditPlus.text_edit)
        self.proj_info_edit.setAlignment(Qt.AlignCenter, LineEditPlus.text_edit)
        self.die_info_edit.setPrefixWidth(prefix_w)
        self.die_info_edit.setPostfixWidth(postfix_w)
        self.die_info_edit.setPlaceholderText("Width",  target = LineEditPlus.text_edit)
        self.die_info_edit.setPlaceholderText("Height", target = LineEditPlus.dual_text_edit)
        self.die_info_edit.setAlignment(Qt.AlignCenter, LineEditPlus.text_edit | LineEditPlus.dual_text_edit)
        self.die_info_edit.setText("x", target = LineEditPlus.seperate_1st_label)
        v = QDoubleValidator(1, 15000, 2)
        v.setNotation(QDoubleValidator.StandardNotation)
        self.die_info_edit.setValidator(v, target = LineEditPlus.text_edit | LineEditPlus.dual_text_edit)

        self.shot_info_edit.setPrefixWidth(prefix_w)
        self.shot_info_edit.setPostfixWidth(postfix_w)
        self.shot_info_edit.setAlignment(Qt.AlignCenter, LineEditPlus.text_edit | LineEditPlus.dual_text_edit)
        self.shot_info_edit.setPlaceholderText("Row",    target = LineEditPlus.text_edit)
        self.shot_info_edit.setPlaceholderText("Column", target = LineEditPlus.dual_text_edit)
        self.shot_info_edit.setText("x", target = LineEditPlus.seperate_1st_label)        
        self.shot_info_edit.setValidator(QIntValidator(1, 100),     target = LineEditPlus.text_edit | LineEditPlus.dual_text_edit)



        self.setLayout(VBox(title, self.proj_info_edit, self.die_info_edit, self.shot_info_edit).setSpacing(20).setContentsMargins(QMargins(0,0,0,0)))
