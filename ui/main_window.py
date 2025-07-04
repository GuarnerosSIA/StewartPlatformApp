from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QAction, QMenu
from PyQt5.QtCore import Qt
from random import choice
import sys



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    def contextMenuEvent(self, event):
        context = QMenu(self)
        context.addAction(QAction("Option 1", self))
        context.addAction(QAction("Option 2", self))
        context.addAction(QAction("Option 3", self))
        context.exec(event.globalPos())



app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()