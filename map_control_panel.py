
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from uiplus import HBox, VBox, LineEditPlus, StepEditPlus, PushButtonPlus, HorizontalLinePlus



class map_control(QWidget):

    def __init__(self, parent=None):
        super(map_control, self).__init__(parent)
        prefix_w, postfix_w  = 115, 85
        title                    = HorizontalLinePlus("Wafer Map adjustment")
        self.zero_mk_combo       = LineEditPlus(prefix = "Zero mark",           postfix = "die²", mode = LineEditPlus.text_edit      | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.ece_pad_combo       = LineEditPlus(prefix = "ECE pad",             postfix = "die²", mode = LineEditPlus.text_edit      | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.edge_exclusion_edit = LineEditPlus(prefix = "EBR width",           postfix = "mm",   mode = LineEditPlus.text_edit      | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.flat_exclusion_edit = LineEditPlus(prefix = "Laser mark height",   postfix = "mm",   mode = LineEditPlus.text_edit      | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.map_shift_edit      = LineEditPlus(prefix = "Map shift x:",           postfix = "um",   mode = LineEditPlus.dual_text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        self.min_die_edit        = LineEditPlus(prefix = "Min die within shot", postfix = "die",  mode = LineEditPlus.text_edit      | LineEditPlus.prefix_label | LineEditPlus.postfix_label)


        self.map_shift_edit.setText(", y:", target = LineEditPlus.seperate_1st_label)

        self.setLayout(VBox(title, self.zero_mk_combo, self.ece_pad_combo, self.edge_exclusion_edit, self.flat_exclusion_edit, self.map_shift_edit, self.min_die_edit).setSpacing(20).setContentsMargins(QMargins(0,0,0,0)))
        self.zero_mk_combo.setPostfixWidth(postfix_w)
        self.ece_pad_combo.setPostfixWidth(postfix_w)
        self.edge_exclusion_edit.setPostfixWidth(postfix_w)
        self.flat_exclusion_edit.setPostfixWidth(postfix_w)
        self.map_shift_edit.setPostfixWidth(postfix_w)
        self.min_die_edit.setPostfixWidth(postfix_w)
        self.zero_mk_combo.setPrefixWidth(prefix_w)
        self.ece_pad_combo.setPrefixWidth(prefix_w)
        self.edge_exclusion_edit.setPrefixWidth(prefix_w)
        self.flat_exclusion_edit.setPrefixWidth(prefix_w)
        self.map_shift_edit.setPrefixWidth(prefix_w)
        self.min_die_edit.setPrefixWidth(prefix_w)
