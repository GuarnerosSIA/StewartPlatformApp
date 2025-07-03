from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow
from PyQt5.QtCore import Qt, QSize
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setFixedSize((QSize(100, 600)))

        # Create a central widget
        button = QPushButton("Click Me")
        self.setCentralWidget(button)
        


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec_()