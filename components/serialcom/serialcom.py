import serial
import serial.tools.list_ports
import time

from PyQt6.QtCore import QThread, pyqtSignal
from components.utils.utils import Utils


class SerialCommunicator:
    def __init__(self):
        self.utils = Utils()
        self.serial_ports = self.get_serial_ports()
        self.ser = None  # Initialize serial object to None

    def get_serial_ports(self):
        """Returns a list of available serial ports."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def get_serial_ports_as_str(self):
        """Returns a list of available serial ports as strings."""
        return self.get_serial_ports()

class SerialReaderThread(QThread):
    data_received = pyqtSignal(str)
    factory_status_changed = pyqtSignal(bool)

    def __init__(self, port, baud):
        super().__init__()
        self.port = port
        self.baud = baud
        self.serial_conn = None
        self.running = True
        self.factory_status = False

    def run(self):
        self.factory_mode()
        self.finished.emit()  # Emit finished signal if needed

    def factory_mode(self):
        try:
            self.factory_status = False
            # Open the serial port
            self.serial_conn = serial.Serial(self.port, self.baud, timeout=1)
            while self.running:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.readline().decode('utf-8').strip()
                    # Emit the signal with the received data
                    self.data_received.emit(data)
                    if data == ".":
                        self.write_data("polyaire&ADT\r\n") # Factory Mode Password
                        self.write_data(" FF:3;RGB-1\r\n") # Set RGB to red for testing
                        self.factory_status = True
                        self.factory_status_changed.emit(self.factory_status)  # Emit status change
        except serial.SerialException as e:
            self.data_received.emit(f"Error: {e}")

    def stop(self):
        self.running = False
        # Ensure to close the serial connection in stop() as well
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.serial_conn = None
    
    def write_data(self, data_to_write):
        """Write data to the serial port."""
        if self.serial_conn and self.serial_conn.is_open:
            print(f"Writing to serial: {data_to_write}")
            self.serial_conn.write(data_to_write.encode('utf-8'))
        else:
            print("Serial port is not open. Cannot write data.")
