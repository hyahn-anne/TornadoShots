import sys
from PyQt5.QtWidgets import QApplication
from tornado_gui import Window

if __name__ == '__main__':
    app = QApplication([])
    win = Window()
    sys.exit(app.exec_())