import subprocess
import configparser
import os
import sqlite3

from typing import List

class Utils:
    def __init__(self, config_file: str = 'config.ini'):
        # Initialize instance variables with default values
        self.tool_path = ''
        self.order_file_path = ''
        self.filepath_firmwareS3 = ''
        self.filepath_certificatesS3 = ''
        self.filepath_firmwareH2 = ''
        
        # Erase flash addresses for ESP32-S3 and ESP32-H2
        self.address_start_erase_flashS3 = ''
        self.address_end_erase_flashS3 = ''
        self.address_start_erase_flashH2 = ''
        self.address_end_erase_flashH2 = ''
        
        # Flash firmware ports for ESP32-S3 and ESP32-H2
        self.port_flashS3 = ''
        self.port_flashH2 = ''
        
        # Flash firmware baud rates for ESP32-S3 and ESP32-H2
        self.baud_flashS3 = ''
        self.baud_flashH2 = ''
        
        # Flash Command
        self.command_flashS3 = ''
        self.command_flashH2 = ''
        
        # Flash firmware addresses for ESP32-S3 and ESP32-H2
        self.address_bootloader_flashS3 = ''
        self.address_partition_table_flashS3 = ''
        self.address_ota_data_initial_flashS3 = ''
        self.address_firmware_flashS3 = ''
        self.address_bootloader_flashH2 = ''
        self.address_partition_table_flashH2 = ''
        self.address_firmware_flashH2 = ''
        
        # Flash DAC addresses ESP32-S3
        self.address_dac_secure_cert_partition = ''
        self.address_dac_data_provider_partition = ''
        
        # Factory port and baud for ESP32-S3
        self.port_factoryS3 = ''
        self.baud_factoryS3 = ''
        
        # Load configuration from the config file
        self.config_reader(config_file)

    def config_reader(self, config_file: str) -> None:
        """
        Reads configuration values from a config.ini file and stores them in instance variables.
        
        Args:
            config_file (str): Path to the configuration file.
        """
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Read values from the config file and store them in instance variables
        self.tool_path = config['DEFAULT'].get('tool_path', self.tool_path)
        self.order_file_path = config['DEFAULT'].get('order_file_path', self.order_file_path)
        
        self.command_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_command', self.command_flashS3)
        self.command_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_command', self.command_flashH2)
        
        self.address_start_erase_flashS3 = config['erase_flash_esp32s3'].get('erase_flash_esp32s3_start_address', self.address_start_erase_flashS3)
        self.address_end_erase_flashS3 = config['erase_flash_esp32s3'].get('erase_flash_esp32s3_end_address', self.address_end_erase_flashS3)
        
        self.address_start_erase_flashH2 = config['erase_flash_esp32h2'].get('erase_flash_esp32h2_start_address', self.address_start_erase_flashS3)
        self.address_end_erase_flashH2 = config['erase_flash_esp32h2'].get('erase_flash_esp32h2_end_address', self.address_end_erase_flashS3)    
    
        self.port_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_port', self.port_flashS3)
        self.port_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_port', self.port_flashH2)
        
        self.baud_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_baud', self.baud_flashS3)
        self.baud_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_baud', self.baud_flashH2)
        
        self.filepath_firmwareS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_filepath', self.filepath_firmwareS3)
        self.address_bootloader_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_bootloader_address', self.address_bootloader_flashS3)
        self.address_partition_table_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_partition_table_address', self.address_partition_table_flashS3)
        self.address_ota_data_initial_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_ota_data_initial_address', self.address_ota_data_initial_flashS3)
        self.address_firmware_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_address', self.address_firmware_flashS3)
        
        self.filepath_firmwareH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_filepath', self.filepath_firmwareH2)
        self.address_bootloader_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_bootloader_address', self.address_bootloader_flashH2)
        self.address_partition_table_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_partition_table_address', self.address_partition_table_flashH2)
        self.address_firmware_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_address', self.address_firmware_flashH2)
        
        self.filepath_certificatesS3 = config['flash_dac_esp32s3'].get('flash_cert_esp32s3_filepath', self.filepath_certificatesS3)
        self.address_dac_secure_cert_partition = config['flash_dac_esp32s3'].get('flash_dac_esp32s3_secure_cert_partition', self.address_dac_secure_cert_partition)
        self.address_dac_data_provider_partition = config['flash_dac_esp32s3'].get('flash_dac_esp32s3_data_provider_partition', self.address_dac_data_provider_partition)
        
        self.port_factoryS3 = config['factory_esp32s3'].get('factory_esp32s3_port', self.port_factoryS3)
        self.baud_factoryS3 = config['factory_esp32s3'].get('factory_esp32s3_baud', self.baud_factoryS3)
        
    def check_functionality(self) -> bool:
        """
        Check if esptool is functioning correctly.

        Returns:
            bool: True if esptool is working, False otherwise.
        """
        try:
            # Attempt to run esptool with no arguments to check if it's available
            result = subprocess.run([self.tool_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Check if esptool provides a help message (i.e., no unrecognized argument errors)
            if "usage:" in result.stdout or "usage:" in result.stderr:
                print("esptool is functioning correctly.")
                return True
            else:
                print("esptool encountered an error:", result.stderr.strip())
                return False

        except FileNotFoundError:
            print("esptool is not installed or not found in the system PATH.")
            return False
        except Exception as e:
            print(f"An error occurred while checking esptool: {e}")
            return False

    def read_order(self, file_path: str = None) -> List[str]:
        """
        Read the order from the given file or from the config file if not provided.

        Args:
            file_path (str, optional): Path to the file containing order numbers.

        Returns:
            List[str]: A list of unique order numbers found in the file.
        """
        if file_path is None:
            file_path = self.order_file_path

        order_numbers = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if 'order-no' in line:
                        order_number = line.split('order-no: ')[1].split(',')[0].strip()
                        if order_number not in order_numbers:
                            order_numbers.append(order_number)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
        
        return order_numbers

    def find_bin_path(self, keyword, search_directory):
        for root, dirs, files in os.walk(search_directory):
            for file in files:
                if file.endswith(".bin") and keyword in file:
                    return os.path.join(root, file)
        return None
    
    def process_device_data(self, device_data_file: str, db_name: str = 'device_data.db') -> None:
        """
        Processes the device data from a file and stores it into an SQLite database.
        
        Args:
            device_data_file (str): Path to the file containing device data.
            db_name (str, optional): Name of the SQLite database file. Defaults to 'device_data.db'.
        """
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                order_no TEXT,
                mac_address TEXT,
                serial_id TEXT,
                cert_id TEXT,
                esp_secure_cert_partition TEXT,
                commissionable_data_provider_partition TEXT,
                qrcode TEXT,
                manualcode TEXT,
                discriminator INTEGER,
                passcode INTEGER
            )
        ''')

        # Read and parse the device data file
        try:
            with open(device_data_file, 'r') as file:
                for line in file:
                    if 'order-no' in line:
                        # Parse each field from the line
                        order_no = line.split('order-no: ')[1].split(',')[0].strip()
                        mac_address = line.split('mac-address: ')[1].split(',')[0].strip()
                        serial_id = line.split('serial-id: ')[1].split(',')[0].strip()
                        cert_id = line.split('cert-id: ')[1].split(',')[0].strip()
                        esp_secure_cert_partition = line.split('esp-secure-cert-partition: ')[1].split(',')[0].strip()
                        commissionable_data_provider_partition = line.split('commissionable-data-provider-partition: ')[1].split(',')[0].strip()
                        qrcode = line.split('qrcode: ')[1].split(',')[0].strip()
                        manualcode = line.split('manualcode: ')[1].split(',')[0].strip()
                        discriminator = int(line.split('discriminator: ')[1].split(',')[0].strip())
                        passcode = int(line.split('passcode: ')[1].strip())

                        # Insert the data into the database
                        cursor.execute('''
                            INSERT INTO devices (order_no, mac_address, serial_id, cert_id, esp_secure_cert_partition,
                                                commissionable_data_provider_partition, qrcode, manualcode, discriminator, passcode)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (order_no, mac_address, serial_id, cert_id, esp_secure_cert_partition,
                                commissionable_data_provider_partition, qrcode, manualcode, discriminator, passcode))

        except FileNotFoundError:
            print(f"File not found: {device_data_file}")
        except Exception as e:
            print(f"An error occurred while processing the device data: {e}")
        finally:
            # Commit the changes and close the database connection
            conn.commit()
            conn.close()
            print("Device data processing complete and stored in the database.")
                        
    def esptool_read_mac(self, port: str, baud: int) -> str:
        """
        Read the MAC address of the ESP32 device using esptool.
        
        Args:
            port (str): Port where the ESP32 device is connected.
            baud (int): Baud rate for the serial communication.
        
        Returns:
            str: MAC address of the ESP32 device.
        """
        try:
            # Run esptool to read the MAC address
            result = subprocess.run(
                [self.tool_path, '--port', port, '--baud', str(baud), 'read_mac'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Extract the MAC address from the output
            for line in result.stdout.splitlines():
                if "MAC:" in line:
                    mac_address = line.split('MAC: ')[1].strip()
                    print(f"MAC address: {mac_address}")
                    return mac_address

            # If MAC address is not found in the output
            print("MAC address not found in the output.")
            return None

        except Exception as e:
            print(f"An error occurred while reading the MAC address: {e}")
            return None
    
    def esptool_reboot(self, port: str, baud: int) -> None:
        """
        Reboot the ESP32 device using esptool.
        
        Args:
            port (str): Port where the ESP32 device is connected.
            baud (int): Baud rate for the serial communication.
        """
        try:
            # Run esptool to reboot the device
            result = subprocess.run(
                [self.tool_path, '--port', port, '--baud', str(baud), 'run'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            print(f"Command output: {result.stdout.strip()}")
            
            # Check if the device is successfully rebooted
            if "Hard resetting via RTS pin..." in result.stdout:
                print("Device rebooted successfully.")
            else:
                print("Device reboot failed.")
                
        except Exception as e:
            print(f"An error occurred while rebooting the device: {e}")
