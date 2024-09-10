import subprocess
import configparser
from typing import List

class Utils:
    def __init__(self, config_file: str = 'config.ini'):
        # Initialize instance variables with default values
        self.tool_path = ''
        self.order_file_path = ''
        
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
        
        self.address_start_erase_flashS3 = config['erase_flash_esp32s3'].get('erase_flash_esp32s3_start_address', self.address_start_erase_flashS3)
        self.address_end_erase_flashS3 = config['erase_flash_esp32s3'].get('erase_flash_esp32s3_end_address', self.address_end_erase_flashS3)
        
        self.address_start_erase_flashH2 = config['erase_flash_esp32h2'].get('erase_flash_esp32h2_start_address', self.address_start_erase_flashS3)
        self.address_end_erase_flashH2 = config['erase_flash_esp32h2'].get('erase_flash_esp32h2_end_address', self.address_end_erase_flashS3)    
    
        self.port_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_port', self.port_flashS3)
        self.port_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_port', self.port_flashH2)
        
        self.baud_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_baud', self.baud_flashS3)
        self.baud_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_baud', self.baud_flashH2)
        
        self.address_bootloader_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_bootloader_address', self.address_bootloader_flashS3)
        self.address_partition_table_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_partition_table_address', self.address_partition_table_flashS3)
        self.address_ota_data_initial_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_ota_data_initial_address', self.address_ota_data_initial_flashS3)
        self.address_firmware_flashS3 = config['flash_firmware_esp32s3'].get('flash_firmware_esp32s3_address', self.address_firmware_flashS3)
        self.address_bootloader_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_bootloader_address', self.address_bootloader_flashH2)
        self.address_partition_table_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_partition_table_address', self.address_partition_table_flashH2)
        self.address_firmware_flashH2 = config['flash_firmware_esp32h2'].get('flash_firmware_esp32h2_address', self.address_firmware_flashH2)
        
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
