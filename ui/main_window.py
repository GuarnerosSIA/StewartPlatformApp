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


class SerialCommunicator(QObject):
    """
    Clase separada para manejar la comunicación serial con hilos
    """
    # Señales para comunicarse con la interfaz gráfica
    connected = pyqtSignal(str)  # Emite cuando se conecta
    disconnected = pyqtSignal()  # Emite cuando se desconecta
    data_received = pyqtSignal(str)  # Emite cuando recibe datos
    error_occurred = pyqtSignal(str)  # Emite cuando hay error
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.stop_reading = False
        
    def get_available_ports(self):
        """Obtener lista de puertos disponibles"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid
            })
        return ports
    
    def connect(self, port, baudrate=115200, timeout=1):
        """Conectar al puerto serial"""
        try:
            if self.is_connected:
                self.disconnect()
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
            )
            
            self.is_connected = True
            self.stop_reading = False
            
            # Iniciar hilo de lectura
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            self.connected.emit(f"Conectado a {port} @ {baudrate} bps")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error de conexión: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconectar del puerto serial"""
        if self.is_connected:
            self.stop_reading = True
            self.is_connected = False
            
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=1)
            
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.disconnected.emit()
    
    def _read_loop(self):
        """Bucle de lectura en hilo separado"""
        while not self.stop_reading and self.is_connected:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode().strip()
                    if data:
                        self.data_received.emit(data)
                        
                time.sleep(0.01)  # Pequeña pausa para no sobrecargar CPU
                
            except Exception as e:
                self.error_occurred.emit(f"Error leyendo datos: {str(e)}")
                break
    
    def send_data(self, data):
        """Enviar datos por serial"""
        if self.is_connected and self.serial_port:
            try:
                if isinstance(data, str):
                    self.serial_port.write(data.encode())
                else:
                    self.serial_port.write(data)
                return True
            except Exception as e:
                self.error_occurred.emit(f"Error enviando datos: {str(e)}")
                return False
        return False


class SerialApp_Stage1(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_comm = SerialCommunicator()
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
        self.baudrate_spin.setRange(300, 115200)
        self.baudrate_spin.setValue(9600)
        
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