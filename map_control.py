
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from uiplus import HBox, VBox



class map_control(QWidget):
    def __init__(self, parent=None):
        super(map_control, self).__init__(parent)
        

        
        m1 = HorizontalLinePlus("Cell / Shot")
        l1 = LineEditPlus(prefix = "Die  size",    postfix = "um²",  mode = LineEditPlus.dual_text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        l2 = LineEditPlus(prefix = "Shot Size",    postfix = "die²", mode = LineEditPlus.dual_text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        l1.setPrefixWidth(100)
        l1.setPostfixWidth(65)
        l1.setPlaceholderText("Width",  target = LineEditPlus.text_edit)
        l1.setPlaceholderText("Height", target = LineEditPlus.dual_text_edit)
        l1.setAlignment(Qt.AlignCenter, LineEditPlus.text_edit | LineEditPlus.dual_text_edit)
        l1.setText("x", target = LineEditPlus.seperate_1st_label)
        l1.setValidator(QDoubleValidator(1, 20000, 2, None), target = LineEditPlus.text_edit | LineEditPlus.dual_text_edit)


        l2.setPrefixWidth(100)
        l2.setPostfixWidth(65)
        l2.setAlignment(Qt.AlignCenter, LineEditPlus.text_edit | LineEditPlus.dual_text_edit)
        l2.setPlaceholderText("Row",   target = LineEditPlus.text_edit)
        l2.setPlaceholderText("Column", target = LineEditPlus.dual_text_edit)
        l2.setText("x", target = LineEditPlus.seperate_1st_label)        
        l2.setValidator(QIntValidator(1, 5000, None),     target = LineEditPlus.text_edit | LineEditPlus.dual_text_edit)

        m2 = HorizontalLinePlus("Exclusion")
        l3 = LineEditPlus(prefix = "Edge exclusion", postfix = "mm",            mode = LineEditPlus.text_edit      | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        l4 = LineEditPlus(prefix = "Flat exclusion", postfix = "mm",            mode = LineEditPlus.text_edit      | LineEditPlus.prefix_label | LineEditPlus.postfix_label)
        l5 = LineEditPlus(prefix = "Zero exclusion", postfix = ["die", "shot"], mode = LineEditPlus.dual_text_edit | LineEditPlus.prefix_label | LineEditPlus.postfix_combo)
        
        l3.setPrefixWidth(100).setPostfixWidth(65)
        l4.setPrefixWidth(100).setPostfixWidth(65)
        l5.setPrefixWidth(100).setPostfixWidth(65)

        l6 = LineEditPlus(text = "test text")
        l7 = LineEditPlus(text = "test text", prefix = "lable",  mode = LineEditPlus.text_edit | LineEditPlus.prefix_label)
        l8 = LineEditPlus(text = "test text", postfix = "lable", mode = LineEditPlus.text_edit | LineEditPlus.postfix_label)
        l9 = LineEditPlus(text = "test text", postfix = "lable", mode = LineEditPlus.tripple_text_edit | LineEditPlus.postfix_label)
        k = PushButtonPlus("update")
        h = VBox(m1, l1, l2, 20, m2, l3, l4, l5, -1, l6, l7, l8, l9,  k)
        h.setSpacing(15)
        
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
        self.h.setContentsMargins(QMargins(0,0,0,0))
        self.setLayout(self.h)

        self.title_label.setObjectName("title")
        self.frame_1.setObjectName("hline")
        self.frame_2.setObjectName("hline")

        self.frame_1.setFrameStyle(QFrame.HLine | QFrame.Plain)
        self.frame_2.setFrameStyle(QFrame.HLine | QFrame.Plain)

        self.frame_1.setLineWidth(1)
        self.frame_2.setLineWidth(1)

        self.frame_1.setMidLineWidth(1)
        self.frame_2.setMidLineWidth(1)        
        self.frame_1.setFixedWidth(5)
        
        self.title_label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))


    def setTitle(self, text):
        self.title_label.setText(title)




class PushButtonPlus(QPushButton):
    def __init__(self, parent=None):
        super(PushButtonPlus, self).__init__(parent)

class LineEditPlus(QWidget):

    prefix_label       = 0x100000000
    text_edit          = 0x010000000
    seperate_1st_label = 0x001000000
    dual_text_edit     = 0x001100000
    seperate_2nd_label = 0x000010000
    tripple_text_edit  = 0x000011000
    postfix_label      = 0x000000100
    postfix_button     = 0x000000010
    postfix_combo      = 0x000000001
    with_postFix       = 0x000000111
    with_preFix        = 0x100000000
    

    def __init__(self, text = "", prefix = "", postfix = "", placeholder = "", mode = text_edit, parent=None):
        super(LineEditPlus, self).__init__(parent)



        self._mode           = mode
        self._prefix_enable  = False
        self._postfix_enable = False
        self._prefix_label   = QLabel(prefix)
        self._postfix_label  = QLabel(postfix if issubclass(type(postfix), str) else "")
        self._postfix_button = QPushButton(postfix if issubclass(type(postfix), str) else "")
        self._postfix_combo  = QComboBox()
        self._1st_line_edit  = QLineEdit(text if issubclass(type(text), str) else text[0])
        self._2nd_line_edit  = QLineEdit(  "" if issubclass(type(text), str) else text[1])
        self._3rd_line_edit  = QLineEdit(  "" if issubclass(type(text), str) else text[2])
        self._1st_seperator  = QLabel()
        self._2nd_seperator  = QLabel()
        self._layout         = HBox()

        self._postfix_combo.addItems(postfix if issubclass(type(postfix), list) else [])
        self._1st_line_edit.setPlaceholderText(placeholder if issubclass(type(placeholder), str) else placeholder[0])
        self._2nd_line_edit.setPlaceholderText(placeholder if issubclass(type(placeholder), str) else placeholder[1])
        self._3rd_line_edit.setPlaceholderText(placeholder if issubclass(type(placeholder), str) else placeholder[2])

        self._prefix_label.setObjectName("prefix_label")
        self._postfix_label.setObjectName("postfix_label")
        self._postfix_button.setObjectName("posfix_button")
        self._postfix_combo.setObjectName("postfix_combo")
        self._1st_line_edit.setObjectName("line_edit")
        self._2nd_line_edit.setObjectName("line_edit")
        self._3rd_line_edit.setObjectName("line_edit")
        self._1st_seperator.setObjectName("seperator_label")
        self._2nd_seperator.setObjectName("seperator_label")

        self._1st_line_edit.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
     
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(QMargins(0,0,0,0))

        self.setMode(mode)
        self.setLayout(self._layout)

    def setMode(self, mode):
        self._mode = mode
        l = []

        self._prefix_enable  = True if (LineEditPlus.with_preFix  & mode == LineEditPlus.with_preFix)  else False
        self._postfix_enable = True if (LineEditPlus.with_postFix & mode == LineEditPlus.with_postFix) else False


        if (LineEditPlus.prefix_label & mode == LineEditPlus.prefix_label):
            l.append(self._prefix_label)

        if (LineEditPlus.tripple_text_edit & mode == LineEditPlus.tripple_text_edit):
            l.append(self._1st_line_edit)
            l.append(self._1st_seperator)
            l.append(self._2nd_line_edit)
            l.append(self._2nd_seperator)
            l.append(self._3rd_line_edit)

        elif (LineEditPlus.dual_text_edit & mode == LineEditPlus.dual_text_edit):
            l.append(self._1st_line_edit)
            l.append(self._1st_seperator)
            l.append(self._2nd_line_edit)

        elif (LineEditPlus.text_edit      & mode == LineEditPlus.text_edit):
            l.append(self._1st_line_edit)


        if   (LineEditPlus.postfix_label  & mode == LineEditPlus.postfix_label):
            l.append(self._postfix_label)

        elif (LineEditPlus.postfix_button & mode == LineEditPlus.postfix_button):
            l.append(self._postfix_button)

        elif (LineEditPlus.postfix_combo  & mode == LineEditPlus.postfix_combo):
            l.append(self._postfix_combo)
            
        if len(l)==1:
            l[0].setProperty('only_one_item', True)
        else:
            for item in l:
                item.setProperty('only_one_item', False)
                item.setProperty('first_item',    False)
                item.setProperty('last_item',     False)
                item.setProperty('middle_item',   True)
            l[0].setProperty('first_item',   True)
            l[0].setProperty('middle_item',  False)
            l[-1].setProperty('last_item',   True)
            l[-1].setProperty('middle_item', False)


        self._layout.setLayoutList(l)

    def setPlaceholderText(self, placeholder, target = text_edit):

        if (LineEditPlus.tripple_text_edit & target == LineEditPlus.tripple_text_edit):
            self._3rd_line_edit.setPlaceholderText(placeholder)

        if (LineEditPlus.dual_text_edit    & target == LineEditPlus.dual_text_edit):
            self._2nd_line_edit.setPlaceholderText(placeholder)

        if (LineEditPlus.text_edit         & target == LineEditPlus.text_edit):
            self._1st_line_edit.setPlaceholderText(placeholder)

        return self

    def setValidator(self, validator, target = text_edit):

        if   (LineEditPlus.tripple_text_edit & target == LineEditPlus.tripple_text_edit):
            self._3rd_line_edit.setValidator(validator)

        if (LineEditPlus.dual_text_edit    & target == LineEditPlus.dual_text_edit):
            self._2nd_line_edit.setValidator(validator)

        if (LineEditPlus.text_edit         & target == LineEditPlus.text_edit):
            self._1st_line_edit.setValidator(validator)

        return self


    def setAlignment(self, alignment, target = text_edit):
        if (LineEditPlus.prefix_label      & target == LineEditPlus.prefix_label):
            self._prefix_label.setAlignment(alignment)

        if (LineEditPlus.postfix_label      & target == LineEditPlus.postfix_label):
            self._postfix_label.setAlignment(alignment)

        if (LineEditPlus.postfix_button     & target == LineEditPlus.postfix_button):
            self._postfix_button.setAlignment(alignment)

        if (LineEditPlus.tripple_text_edit  & target == LineEditPlus.tripple_text_edit):
            self._3rd_line_edit.setAlignment(alignment)

        if (LineEditPlus.dual_text_edit     & target == LineEditPlus.dual_text_edit):
            self._2nd_line_edit.setAlignment(alignment)

        if (LineEditPlus.text_edit          & target == LineEditPlus.text_edit):
            self._1st_line_edit.setAlignment(alignment)
        
        if (LineEditPlus.seperate_1st_label & target == LineEditPlus.seperate_1st_label):
            self._1st_seperator.setAlignment(alignment)

        if (LineEditPlus.seperate_2nd_label & target == LineEditPlus.seperate_2nd_label):
            self._2nd_seperator.setAlignment(alignment)

        return self        

    def setPostfixText(self, postfix):
        self._postfix_label.setText(postfix)
        return self

    def setPrefixText(self, prefix):
        self._prefix_label.setText(prefix)
        return self
    
    def setText(self, text, target = text_edit):

        if (LineEditPlus.tripple_text_edit  & target == LineEditPlus.tripple_text_edit):
            self._3rd_line_edit.setText(text)

        if (LineEditPlus.dual_text_edit     & target == LineEditPlus.dual_text_edit):
            self._2nd_line_edit.setText(text)

        if (LineEditPlus.text_edit          & target == LineEditPlus.text_edit):
            self._1st_line_edit.setText(text)
        
        if (LineEditPlus.seperate_1st_label & target == LineEditPlus.seperate_1st_label):
            self._1st_seperator.setText(text)

        if (LineEditPlus.seperate_2nd_label & target == LineEditPlus.seperate_2nd_label):
            self._2nd_seperator.setText(text)

        return self

    def text(self, target = text_edit):
        
        if (LineEditPlus.tripple_text_edit  & target == LineEditPlus.tripple_text_edit):
            return self._3rd_line_edit.text()

        if (LineEditPlus.dual_text_edit     & target == LineEditPlus.dual_text_edit):
            return self._2nd_line_edit.text()

        if (LineEditPlus.text_edit          & target == LineEditPlus.text_edit):
            return self._1st_line_edit.text()
        
        if (LineEditPlus.seperate_1st_label & target == LineEditPlus.seperate_1st_label):
            return self._1st_seperator.text()

        if (LineEditPlus.seperate_2nd_label & target == LineEditPlus.seperate_2nd_label):
            return self._2nd_seperator.text()

        return self

    def postfixText(self):
        return self._postfix_label.text()

    def prefixText(self):
        return self._prefix_label.text()

    def setPrefixWidth(self, width):
        self._prefix_label.setFixedWidth(width)
        return self

    def setTextEditWidth(self, width):
        self._1st_line_edit.setFixedWidth(width)
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

