from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Slider:
    def __init__(self, is_float=False):
        super().__init__()
        self.slider = None
        self.label = None
        self.is_float = is_float
    
    
    def create_slide_panel(self, label, min_value, max_value):
        hbox = QHBoxLayout()
        slider_label = QLabel(label)
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setMinimum(min_value)
        self.slider.setMaximum(max_value)
        self.slider.setValue(0.0)
        self.slider.valueChanged.connect(lambda: self.change_slider(min_value, max_value))
        self.label = QLabel()
        if self.is_float:
            default = ((max_value - min_value)/2) + min_value
            self.label.setText(str(float(default / 10)))
            self.slider.setValue(default)
        else:
            self.label.setText(str(0))
        hbox.addWidget(slider_label)
        hbox.addWidget(self.slider)
        hbox.addWidget(self.label)
        return hbox
    

    def change_slider(self, min_value, max_value):
        value = self.slider.value()
        if self.is_float:
            self.label.setText(str(float(value/10)))
        else:
            self.label.setText(str(value))


    def get_value(self):
        return self.slider.value()


    def set_value(self, value):
        self.slider.setValue(value)


class RectArea:
    def __init__(self):
        super().__init__()
        self.label_area = None
        self.btn_set_area = None
        self.btn_reset = None
    

    def create_area(self, label):
        h_area = QHBoxLayout()
        title = QLabel(label)
        title.setFixedWidth(50)
        self.btn_set_area = QPushButton('Set Area')
        self.btn_set_area.setFixedHeight(25)
        self.btn_reset =  QPushButton('Reset')
        self.btn_reset.setFixedHeight(25)
        self.label_area = QLabel()
        self.label_area.setFixedWidth(200)
        h_area.addWidget(title)
        h_area.addWidget(self.btn_set_area)
        h_area.addWidget(self.btn_reset)
        h_area.addWidget(self.label_area)
        return h_area


class TextBox:
    def __init__(self):
        super().__init__()
    

    def create_textbox_panel(self, label1='min', label2='max'):
        h_area = QHBoxLayout()
        label1 = QLabel(label1)
        label1.setAlignment(Qt.AlignCenter)
        label1.setFixedSize(QSize(60, 25))
        self.edit_min = QTextEdit()
        self.edit_min.setFixedHeight(27)
        label2 = QLabel(label2)
        label2.setAlignment(Qt.AlignCenter)
        label2.setFixedSize(QSize(60, 25))
        self.edit_max = QTextEdit()
        self.edit_max.setFixedHeight(27)

        h_area.addWidget(label1)
        h_area.addWidget(self.edit_min)
        h_area.addWidget(label2)
        h_area.addWidget(self.edit_max)

        return h_area


    def get_text(self):
        return (self.edit_min.toPlainText(), self.edit_max.toPlainText())


    def set_text(self, min, max):
        self.edit_min.setText(str(min))
        self.edit_max.setText(str(max))


    def set_resolution(self, res):
        self.edit_max.setText(str(res))