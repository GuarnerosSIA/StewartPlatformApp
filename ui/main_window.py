from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QLabel, QPushButton, QComboBox, 
                             QTextEdit, QSpinBox, QHBoxLayout, QGroupBox, 
                             QSlider, QCheckBox, QGridLayout)
from PyQt5.QtCore import Qt
from communication.serial_handler import SerialCommunicator
import sys



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
        self.setGeometry(100, 100, 600, 400)
        
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
        
        # NUEVO: Grupo de múltiples canales
        channels_group = QGroupBox("Control de Canales")
        channels_layout = QGridLayout()
        
        self.sliders = []
        self.labels = []
        self.checkboxes = []
        
        # Crear 4 canales
        for i in range(6):
            # Checkbox para habilitar canal
            checkbox = QCheckBox(f"Motor {i}")
            checkbox.setChecked(True)
            
            # Slider
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 500)
            slider.setValue(0)
            slider.valueChanged.connect(lambda v, idx=i: self.on_channel_changed(idx, v))
            
            # Label con valor
            label = QLabel("0")
            label.setMinimumWidth(40)
            label.setAlignment(Qt.AlignCenter)
            
            # Agregar a la grilla
            channels_layout.addWidget(checkbox, i, 0)
            channels_layout.addWidget(slider, i, 1)
            channels_layout.addWidget(label, i, 2)
            
            self.sliders.append(slider)
            self.labels.append(label)
            self.checkboxes.append(checkbox)
        
        channels_group.setLayout(channels_layout)
        layout.addWidget(channels_group)
        
        # Grupo de controles de envío
        send_group = QGroupBox("Controles de Envío")
        send_layout = QHBoxLayout()
        
        # Botones de envío
        self.send_all_btn = QPushButton("Enviar Todos")
        self.send_selected_btn = QPushButton("Enviar Seleccionados")
        self.send_individual_btn = QPushButton("Envío Individual")
        
        self.send_all_btn.clicked.connect(self.send_all_values)
        self.send_selected_btn.clicked.connect(self.send_selected_values)
        self.send_individual_btn.clicked.connect(self.toggle_individual_send)
        
        # Checkbox para envío automático
        self.auto_send_cb = QCheckBox("Envío automático")
        self.auto_send_cb.stateChanged.connect(self.toggle_auto_send)
        
        send_layout.addWidget(self.send_all_btn)
        send_layout.addWidget(self.send_selected_btn)
        send_layout.addWidget(self.send_individual_btn)
        send_layout.addWidget(self.auto_send_cb)
        
        send_group.setLayout(send_layout)
        layout.addWidget(send_group)

        # Grupo de conexión
        read_group = QGroupBox("Lectura de Datos")
        read_layout = QHBoxLayout()
        self.read_data = QTextEdit()
        self.read_data.setReadOnly(True)
        read_layout.addWidget(self.read_data)
        read_group.setLayout(read_layout)
        layout.addWidget(read_group)

        
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

    def on_slider_changed(self, value):
        """Cuando cambia el slider"""
        self.value_label.setText(str(value))
        
        # Si está activado el envío automático, enviar inmediatamente
        if self.auto_send_cb.isChecked():
            self.send_current_value()

    def on_channel_changed(self, channel, value):
        """Cuando cambia un canal"""
        self.labels[channel].setText(str(value))
        
        # Si está en modo envío automático, enviar
        if self.auto_send_cb.isChecked():
            if self.individual_send_mode:
                # Enviar solo este canal
                self.serial_comm.send_channel_value(channel, value)
            else:
                # Enviar todos los seleccionados
                self.send_selected_values()

    def send_all_values(self):
        """Enviar todos los valores"""
        values = [int(slider.value()) for slider in self.sliders]
        self.serial_comm.send_data(values)
        self.monitor.append(f"Enviando todos: {values}")
    
    def send_selected_values(self):
        """Enviar solo los canales seleccionados"""
        selected_values = []
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                selected_values.append(self.sliders[i].value())
        
        if selected_values:
            self.serial_comm.send_multiple_values(selected_values)
            self.monitor.append(f"Enviando seleccionados: {selected_values}")
        else:
            self.monitor.append("No hay canales seleccionados")
    
    def send_current_value(self):
        """Enviar el valor actual del slider"""
        value = self.value_slider.value()
        values_received = self.serial_comm.send_single_value(value)
        self.read_data.append(f"Enviado: {values_received}")
    
    def toggle_individual_send(self):
        """Alternar modo de envío individual"""
        self.individual_send_mode = not self.individual_send_mode
        
        if self.individual_send_mode:
            self.send_individual_btn.setText("Envío Individual ✓")
            self.send_individual_btn.setStyleSheet("background-color: lightgreen;")
            self.monitor.append("Modo envío individual activado")
        else:
            self.send_individual_btn.setText("Envío Individual")
            self.send_individual_btn.setStyleSheet("")
            self.monitor.append("Modo envío individual desactivado")

    def toggle_auto_send(self, state):
        """Alternar envío automático"""
        if state == Qt.Checked:
            self.send_btn.setEnabled(False)
            self.monitor.append("Envío automático activado")
        else:
            self.send_btn.setEnabled(True)
            self.monitor.append("Envío automático desactivado")
    
    def on_data_received(self, data):
        """Cuando se reciben datos"""
        self.monitor.append(f"Recibido: {data}")
    
    def on_data_sent(self, data):
        """Cuando se envían datos"""
        self.monitor.append(f"Enviado: {data.strip()}")
    
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