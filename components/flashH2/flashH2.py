from PyQt6.QtCore import QThread, pyqtSignal
import subprocess
from components.utils.utils import Utils

class FlashFirmwareH2Thread(QThread):
    finished = pyqtSignal()
    show_message = pyqtSignal(str, str)  # Signal for showing messages

    def __init__(self, port, baud, bootloader_address, partition_table_address, firmware_address):
        super().__init__()
        self.utils = Utils()
        self.port = port
        self.baud = baud
        self.bootloader_address = bootloader_address
        self.partition_table_address = partition_table_address
        self.firmware_address = firmware_address

    def run(self):
        """Runs the firmware flashing processes."""      
        # Flash firmware
        if not self.flash_firmware():
            self.show_message.emit("Error", "Firmware flashing failed.")
            self.finished.emit()
            return
        
        self.show_message.emit("Success", "H2 Firmware flashing completed successfully!")
        self.finished.emit()

    def flash_firmware(self):
        """Flashes the firmware."""
        print(f"Address Bootloader: {self.bootloader_address}")
        print(f"Address Partition Table: {self.partition_table_address}")
        print(f"Address Firmware: {self.firmware_address}")

        command = [
            'esptool.py',
            '--port', self.port,
            '--baud', self.baud,
            'write_flash',
            self.bootloader_address, self.utils.find_bin_path('bootloader', self.utils.filepath_firmwareH2),
            self.partition_table_address, self.utils.find_bin_path('partition-table', self.utils.filepath_firmwareH2),
            self.firmware_address, self.utils.find_bin_path('H2', self.utils.filepath_firmwareH2)
        ]
        
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            success_detected = False
            for line in process.stdout:
                print(line, end='')
                if "Hard resetting via RTS pin..." in line:
                    success_detected = True
            process.wait()
            if process.returncode != 0:
                error_output = process.stderr.read()
                self.show_message.emit("Error", f"An error occurred while flashing the firmware: {error_output}")
                return False
            return success_detected
        except Exception as e:
            self.show_message.emit("Error", f"An unexpected error occurred: {str(e)}")
            return False