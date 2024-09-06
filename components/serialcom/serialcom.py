import serial.tools.list_ports

class SerialCommunicator:
    def __init__(self):
        self.serial_ports = self.get_serial_ports()

    def get_serial_ports(self):
        """Returns a list of available serial ports."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def get_serial_ports_as_str(self):
        """Returns a list of available serial ports as strings."""
        return self.get_serial_ports()
