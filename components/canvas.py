from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Canvas(QLabel):
    drawing_mode = False
    flag = False
    xmin = 0
    ymin = 0
    xmax = 0
    ymax = 0
    rectangles = []
    color = Qt.white
    label = None
    tag = None


    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(self.color, 2, Qt.SolidLine))

        for rect, tag in self.rectangles:
            painter.drawRect(rect)

        if self.flag:
            rect = QRect(self.xmin, self.ymin, abs(self.xmax - self.xmin), abs(self.ymax - self.ymin))
            painter.drawRect(rect)


    def mousePressEvent(self, event):
        if self.drawing_mode:
            if event.buttons() & Qt.LeftButton:
                self.flag = True
                self.xmin = event.x()
                self.ymin = event.y()


    def mouseMoveEvent(self, event):
        if self.drawing_mode:
            if event.buttons() & Qt.LeftButton:
                if self.flag:
                    self.xmax = event.x()
                    self.ymax = event.y()
                    self.override_cursor(Qt.CrossCursor)
                    self.update()


    def mouseReleaseEvent(self, event):
        if self.drawing_mode:
            r = QRect(self.xmin, self.ymin, abs(self.xmax - self.xmin), abs(self.ymax - self.ymin))
            self.rectangles.append((r, self.tag))
            self.label.setText('(%d, %d) (%d, %d)' % (self.xmin, self.ymin, self.xmax, self.ymax))
        self.flag = False
        self.drawing_mode = False
        self.override_cursor(Qt.ArrowCursor)
        self.update()
        super().mouseReleaseEvent(event)


    def set_drawing_mode(self, drawing_mode):
        self.drawing_mode = drawing_mode

    
    def reset(self, label_widget, tag):
        if len(self.rectangles) > 0:
            idx = [r[1] for r in self.rectangles].index(tag)
            self.rectangles.pop(idx)
            label_widget.setText('')
            self.update()


    def current_cursor(self):
        cursor = QApplication.overrideCursor()
        if cursor is not None:
            cursor = cursor.shape()
        return cursor


    def override_cursor(self, cursor):
        self._cursor = cursor
        if self.current_cursor() is None:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.changeOverrideCursor(cursor)
    

    def set_label(self, label_widget):
        self.label = label_widget
    

    def set_tag(self, tag):
        self.tag = tag
    

    def get_rects(self):
        return [(r[0].getRect(), r[1]) for r in self.rectangles]