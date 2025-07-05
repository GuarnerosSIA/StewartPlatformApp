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
    
    def connect(self, port, baudrate=250000, timeout=1):
        """Conectar al puerto serial"""
        try:
            if self.is_connected:
                self.disconnect()
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
            )
            
            time.sleep(3)  # Esperar a que el puerto se estabilice
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
                data_to_send = ','.join(map(str, [255,255,255,255,255,255])) + '\n'
                print(f"Enviando: {data_to_send}")
                self.serial_port.write(data_to_send.encode('utf-8'))
                time.sleep(0.1)
                data_received = self.serial_port.readline()
                print(f"Datos recibidos: {data_received}")
                print(data_received.decode('utf-8'))
                  # Pequeña pausa para no sobrecargar CPU
                
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