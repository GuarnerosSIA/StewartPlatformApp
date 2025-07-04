from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QTextEdit
from PyQt5.QtCore import Qt
from random import choice
import sys



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.label = QLabel("Click this window")
        self.label.setMouseTracking(True)
        self.setCentralWidget(self.label)


    def mouseMoveEvent(self,e):
        self.label.setText("Mouse moved")
    def moursePressEvent(self, e):
        self.label.setText("Mouse pressed")
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.label.setText("Left mouse button released")
        elif e.button() == Qt.RightButton:
            self.label.setText("Right mouse button released")
        elif e.button() == Qt.MiddleButton:
            self.label.setText("Mouse button released")
    def mouseDoubleClickEvent(self, e):
        self.label.setText("Mouse double clicked")



app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()