from PyQt6.QtCore import QThread, pyqtSignal
import subprocess
from components.utils.utils import Utils

class FlashFirmwareAndCertThread(QThread):
    finished = pyqtSignal()
    show_message = pyqtSignal(str, str)  # Signal for showing messages

    def __init__(self, port, baud, bootloader_address, partition_table_address, ota_data_address, firmware_address, secure_cert_partition_address, data_provider_partition_address):
        super().__init__()
        self.utils = Utils()
        self.port = port
        self.baud = baud
        self.bootloader_address = bootloader_address
        self.partition_table_address = partition_table_address
        self.ota_data_address = ota_data_address
        self.firmware_address = firmware_address
        self.secure_cert_partition_address = secure_cert_partition_address
        self.data_provider_partition_address = data_provider_partition_address
        self.success_detected_firmware = False  # Initialize instance variable
        self.success_detected_certificate = False  # Initialize instance variable

    def run(self):
        """Runs the firmware and certificate flashing processes."""
        # Flash certificate
        if not self.flash_certificate():
            self.show_message.emit("Error", "Certificate flashing failed.")
            self.finished.emit()
            return        
        
        # Flash firmware
        if not self.flash_firmware():
            self.show_message.emit("Error", "Firmware flashing failed.")
            self.finished.emit()
            return
        
        self.show_message.emit("Success", "Firmware and certificate flashing completed successfully!")
        self.finished.emit()

    def flash_firmware(self):
        """Flashes the firmware."""
        print(f"Address Bootloader: {self.bootloader_address}")
        print(f"Address Partition Table: {self.partition_table_address}")
        print(f"Address OTA Data Initial: {self.ota_data_address}")
        print(f"Address Firmware: {self.firmware_address}")

        command = [
            'esptool.py',
            '--port', self.port,
            '--baud', self.baud,
            'write_flash',
            self.bootloader_address, self.utils.find_bin_path('bootloader', self.utils.filepath_firmwareS3),
            self.partition_table_address, self.utils.find_bin_path('partition-table', self.utils.filepath_firmwareS3),
            self.ota_data_address, self.utils.find_bin_path('ota_data_initial', self.utils.filepath_firmwareS3),
            self.firmware_address, self.utils.find_bin_path('rc', self.utils.filepath_firmwareS3)
        ]
        
        print(f"Command: {' '.join(command)}")
        
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.success_detected_firmware = False  # Reset success_detected before starting
            for line in process.stdout:
                print(line, end='')
                if "Hard resetting via RTS pin..." in line:
                    self.success_detected_firmware = True
            process.wait()
            if process.returncode != 0:
                error_output = process.stderr.read()
                self.show_message.emit("Error", f"An error occurred while flashing the firmware: {error_output}")
                return False
            return self.success_detected_firmware
        except Exception as e:
            self.show_message.emit("Error", f"An unexpected error occurred: {str(e)}")
            return False

    def flash_certificate(self):
        """Runs the certificate flashing process."""
        print(f"Address Secure Cert Partition: {self.secure_cert_partition_address}")
        print(f"Address Data Provider Partition: {self.data_provider_partition_address}")
        
        # Construct the esptool command
        command = [
            'esptool.py',
            '--port', self.port,
            '--baud', self.baud,
            'write_flash',
            self.secure_cert_partition_address, self.utils.find_bin_path('secure_cert', self.utils.filepath_certificatesS3),
            self.data_provider_partition_address, self.utils.find_bin_path('partition', self.utils.filepath_certificatesS3)
        ]
        
        print(f"Command: {command}")
        
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.success_detected_certificate = False  # Reset success_detected before starting
            for line in process.stdout:
                print(line, end='')
                if "Hard resetting via RTS pin..." in line:
                    self.success_detected_certificate = True
            process.wait()
            if process.returncode != 0:
                error_output = process.stderr.read()
                self.show_message.emit("Error", f"An error occurred while flashing the certificate: {error_output}")
                return False
            return self.success_detected_certificate
        except Exception as e:
            self.show_message.emit("Error", f"An unexpected error occurred: {str(e)}")
            return False
class FlashFirmwareH2Thread(QThread):
    finished = pyqtSignal()
    show_message = pyqtSignal(str, str)  # Signal for showing messages

    def __init__(self, port, baud, command, bootloader_address, partition_table_address, firmware_address):
        super().__init__()
        self.utils = Utils()
        self.port = port
        self.baud = baud
        self.command = command
        self.bootloader_address = bootloader_address
        self.partition_table_address = partition_table_address
        self.firmware_address = firmware_address
        self.success_detected = False  # Initialize instance variable

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
            self.command,
            self.bootloader_address, self.utils.find_bin_path('bootloader', self.utils.filepath_firmwareH2),
            self.partition_table_address, self.utils.find_bin_path('partition-table', self.utils.filepath_firmwareH2),
            self.firmware_address, self.utils.find_bin_path('H2', self.utils.filepath_firmwareH2)
        ]
        
        print(f"Command: {command}")
        
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.success_detected = False  # Reset success_detected before starting
            for line in process.stdout:
                print(line, end='')
                if "Hard resetting via RTS pin..." in line:
                    self.success_detected = True
            process.wait()
            if process.returncode != 0:
                error_output = process.stderr.read()
                self.show_message.emit("Error", f"An error occurred while flashing the certificate: {error_output}")
                return False
            return self.success_detected
        except Exception as e:
            self.show_message.emit("Error", f"An unexpected error occurred: {str(e)}")
            return False