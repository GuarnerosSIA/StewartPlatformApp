from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QAction, QMenu
from PyQt5.QtCore import Qt
from random import choice
import sys



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.show()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
    def on_context_menu(self, event):
        context = QMenu(self)
        context.addAction(QAction("Action 1", self))
        context.addAction(QAction("Action 2", self))
        context.addAction(QAction("Action 3", self))
        context.exec(self.mapToGlobal(event))




app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()