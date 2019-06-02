
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from uiplus import HBox, VBox, LineEditPlus, StepEditPlus, PushButtonPlus, HorizontalLinePlus



class map_control(QWidget):

    def __init__(self, parent=None):
        super(map_control, self).__init__(parent)
        prefix_w, postfix_w  = 115, 85
        title_1                  = HorizontalLinePlus("Wafer Map setup")
        title_2                  = HorizontalLinePlus("Wafer Map shift")
        self.zero_mk_combo       = LineEditPlus(prefix = "Zero mark",           postfix = "die²", mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.ece_pad_combo       = LineEditPlus(prefix = "ECE pad",             postfix = "die²", mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.edge_exclusion_edit = LineEditPlus(prefix = "EBR width",           postfix = "mm",   mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.flat_exclusion_edit = LineEditPlus(prefix = "Laser mark height",   postfix = "mm",   mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.min_die_edit        = LineEditPlus(prefix = "Min die within shot", postfix = "die",  mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.map_shift_edit_x    = LineEditPlus(prefix = "Map shift x:",        postfix = "um",   mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.map_shift_edit_y    = LineEditPlus(prefix = "Map shift y:",        postfix = "um",   mode = LineEditPlus.text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)



        

        self.setLayout(VBox(title_1, self.zero_mk_combo, self.ece_pad_combo, self.edge_exclusion_edit, self.flat_exclusion_edit,  self.min_die_edit, 30, title_2, self.map_shift_edit_x, self.map_shift_edit_y).setSpacing(20).setContentsMargins(QMargins(0,0,0,0)))
        self.zero_mk_combo.setPostfixWidth(postfix_w)
        self.ece_pad_combo.setPostfixWidth(postfix_w)
        self.edge_exclusion_edit.setPostfixWidth(postfix_w)
        self.flat_exclusion_edit.setPostfixWidth(postfix_w)
        self.map_shift_edit_x.setPostfixWidth(postfix_w)
        self.map_shift_edit_y.setPostfixWidth(postfix_w)
        self.min_die_edit.setPostfixWidth(postfix_w)
        self.zero_mk_combo.setPrefixWidth(prefix_w)
        self.ece_pad_combo.setPrefixWidth(prefix_w)
        self.edge_exclusion_edit.setPrefixWidth(prefix_w)
        self.flat_exclusion_edit.setPrefixWidth(prefix_w)
        self.map_shift_edit_x.setPrefixWidth(prefix_w)
        self.map_shift_edit_y.setPrefixWidth(prefix_w)
        self.min_die_edit.setPrefixWidth(prefix_w)
