from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QLabel, QPushButton, QComboBox, 
                             QTextEdit, QSpinBox, QHBoxLayout, QGroupBox)
from PyQt5.QtCore import Qt
from communication.serial_handler import SerialCommunicator
import sys
import serial
import serial.tools.list_ports
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal



class SerialApp_Stage1(QMainWindow):
    def __init__(self, serial_comm=None):
        super().__init__()
        self.serial_comm = serial_comm
        self.setup_signals()
        self.init_ui()
        
    def setup_signals(self):
        """Conectar señales de la clase serial"""
        self.serial_comm.connected.connect(self.on_connected)
        self.serial_comm.disconnected.connect(self.on_disconnected)
        self.serial_comm.data_received.connect(self.on_data_received)
        self.serial_comm.error_occurred.connect(self.on_error)
        
    def init_ui(self):
        self.setWindowTitle('Etapa 1: Conexión Serial')
        self.setGeometry(100, 100, 500, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Grupo de conexión
        conn_group = QGroupBox("Conexión")
        conn_layout = QHBoxLayout()
        
        # Puerto
        self.port_combo = QComboBox()
        self.refresh_ports()
        
        # Baudrate
        self.baudrate_spin = QSpinBox()
        self.baudrate_spin.setRange(300, 2000000)
        self.baudrate_spin.setValue(250000)
        
        # Botones
        self.refresh_btn = QPushButton("Refrescar")
        self.connect_btn = QPushButton("Conectar")
        self.disconnect_btn = QPushButton("Desconectar")
        
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.connect_btn.clicked.connect(self.connect_serial)
        self.disconnect_btn.clicked.connect(self.disconnect_serial)
        
        conn_layout.addWidget(QLabel("Puerto:"))
        conn_layout.addWidget(self.port_combo)
        conn_layout.addWidget(QLabel("Baudrate:"))
        conn_layout.addWidget(self.baudrate_spin)
        conn_layout.addWidget(self.refresh_btn)
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.disconnect_btn)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Status
        self.status_label = QLabel("Desconectado")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Monitor
        self.monitor = QTextEdit()
        self.monitor.setReadOnly(True)
        layout.addWidget(self.monitor)
        
        # Estado inicial
        self.disconnect_btn.setEnabled(False)
        
    def refresh_ports(self):
        """Refrescar puertos disponibles"""
        self.port_combo.clear()
        ports = self.serial_comm.get_available_ports()
        for port in ports:
            self.port_combo.addItem(f"{port['device']} - {port['description']}")
    
    def connect_serial(self):
        """Conectar al puerto serial"""
        port_text = self.port_combo.currentText()
        if not port_text:
            self.monitor.append("Error: No hay puertos disponibles")
            return
        
        port = port_text.split(' - ')[0]
        baudrate = self.baudrate_spin.value()
        
        if self.serial_comm.connect(port, baudrate):
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
    
    def disconnect_serial(self):
        """Desconectar del puerto serial"""
        self.serial_comm.disconnect()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
    
    def on_connected(self, message):
        """Cuando se conecta exitosamente"""
        self.status_label.setText("Conectado")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.monitor.append(message)
    
    def on_disconnected(self):
        """Cuando se desconecta"""
        self.status_label.setText("Desconectado")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.monitor.append("Desconectado")
    
    def on_data_received(self, data):
        """Cuando se reciben datos"""
        self.monitor.append(f"Recibido: {data}")
    
    def on_error(self, error_msg):
        """Cuando ocurre un error"""
        self.monitor.append(f"ERROR: {error_msg}")
        self.status_label.setText("Error")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
    
    def closeEvent(self, event):
        """Al cerrar la aplicación"""
        self.serial_comm.disconnect()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SerialApp_Stage1()
    window.show()
    sys.exit(app.exec_())