from PyQt6.QtCore import QThread, pyqtSignal
from components.utils.utils import Utils
import subprocess


class FlashCertificates(QThread):
    finished = pyqtSignal()
    show_message = pyqtSignal(str, str)  # Signal for showing messages

    def __init__(self, port, baud, secure_cert_partition, data_provider_partition):
        super().__init__()
        self.utils = Utils()
        self.port = port
        self.baud = baud
        self.secure_cert_partition = secure_cert_partition
        self.data_provider_partition = data_provider_partition

    def run(self):
        """Runs the certificate flashing process."""
        print(f"Address Secure Cert Partition: {self.secure_cert_partition}")
        print(f"Address Data Provider Partition: {self.data_provider_partition}")
        
        # Construct the esptool command
        command = [
            'esptool.py',
            '--port', self.port,
            '--baud', self.baud,
            'write_flash',
            self.secure_cert_partition, self.utils.find_bin_path('secure_cert', self.utils.filepath_certificatesS3),
            self.data_provider_partition, self.utils.find_bin_path('partition', self.utils.filepath_certificatesS3)
        ]
        
        print(f"Command: {command}")
            
        try:
            # Start the process
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        
            success_detected = False

            # Read output in real-time
            for line in process.stdout:
                print(line, end='')  # Print the output line-by-line
                if "Hard resetting via RTS pin..." in line:
                    success_detected = True

            # Wait for the process to complete
            process.wait()

            # Check for errors
            if process.returncode != 0:
                error_output = process.stderr.read()
                self.show_message.emit("Error", f"An error occurred while flashing the certificates: {error_output}")

            # Show success message if successful
            if success_detected:
                self.show_message.emit("Success", "Certificates flashing completed successfully!")

        except Exception as e:
            self.show_message.emit("Error", f"An unexpected error occurred: {str(e)}")
            print(f"An unexpected error occurred: {str(e)}")
        finally:
            self.finished.emit()