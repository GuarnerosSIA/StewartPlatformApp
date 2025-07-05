from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QLabel, QPushButton, QComboBox, 
                             QTextEdit, QSpinBox, QHBoxLayout, QGroupBox)
import sys
from ui.main_window import SerialApp_Stage1

app = QApplication(sys.argv)
window = SerialApp_Stage1()
window.show()
sys.exit(app.exec_())
