from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QLabel, QPushButton, QComboBox, 
                             QTextEdit, QSpinBox, QHBoxLayout, QGroupBox)
import sys
from ui.main_window import SerialApp_Stage1
from communication.serial_handler import SerialCommunicator

app = QApplication(sys.argv)
ser = SerialCommunicator()
window = SerialApp_Stage1(serial_comm=ser)
window.show()
sys.exit(app.exec_())
