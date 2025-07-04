from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QSize
from random import choice
import sys

windows_titles = [
    "Welcome to the App",
    "Main Application Window",
    "User Interface",
    "Application Dashboard",
    "Interactive Window",
    "Something went wrong"
    ]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")

        self.label = QLabel()
        
        self.input = QLineEdit()
        self.input.textChanged.connect(self.label.setText)

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)



app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec_()