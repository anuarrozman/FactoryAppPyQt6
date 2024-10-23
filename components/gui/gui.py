from PyQt6.QtWidgets import QMainWindow, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox, QSizePolicy, QGroupBox
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt
from components.serialcom.serialcom import SerialCommunicator, SerialReaderThread
from components.utils.utils import Utils
from components.flash.flash import FlashFirmwareS3Thread, FlashFirmwareH2Thread
class SerialPortSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Port Selector")
        self.setGeometry(100, 100, 800, 600)  # Set initial size and position of the window
        
        # Create instances of Utils and SerialCommunicator
        self.utils = Utils()
        self.serialcom = SerialCommunicator()
        
        # Initialization
        self.serial_thread = None

        # Create GUI components
        self.flash_port_label = self.create_label("ESP32S3 Flash Port    :")
        self.flash_port_combo_box = self.create_combo_box(self.serialcom.get_serial_ports_as_str())
        self.flash_baud_rate_label = self.create_label("Baud Rate:")
        self.flash_baud_rate_combo_box = self.create_baud_rate_combo_box()

        self.factory_port_label = self.create_label("ESP32S3 Factory Port:")
        self.factory_port_combo_box = self.create_combo_box(self.serialcom.get_serial_ports_as_str())
        self.factory_baud_rate_label = self.create_label("Baud Rate:")
        self.factory_baud_rate_combo_box = self.create_baud_rate_combo_box()

        self.h2_flash_port_label = self.create_label("ESP32H2 Flash Port    :")
        self.h2_flash_port_combo_box = self.create_combo_box(self.serialcom.get_serial_ports_as_str())
        self.h2_flash_baud_rate_label = self.create_label("Baud Rate:")
        self.h2_flash_baud_rate_combo_box = self.create_baud_rate_combo_box()

        self.order_id_label = self.create_label("Order ID:")
        self.order_id_combo_box = self.create_combo_box(self.utils.read_order('device_data.txt'))
        
        # Connect signal to print selected order ID
        self.order_id_combo_box.currentIndexChanged.connect(self.print_selected_order_id)
        
        # Group 1: Semi Auto Test
        self.semi_auto_test_label = self.create_label("Semi Auto Test")
        self.semi_auto_test_group = self.create_group_box(self.semi_auto_test_label, "semi_auto_test")
        
        # Group 2: Manual Test
        self.manual_test_label = self.create_label("Manual Test")
        self.manual_test_group = self.create_group_box(self.manual_test_label, "manual_test")
        
        # Group 3: Wi-Fi Test
        self.wifi_test_label = self.create_label("Wi-Fi Test")
        self.wifi_test_group = self.create_group_box(self.wifi_test_label, "wifi_test")
        
        # Group 4: ESP32H2 Test
        self.esp32h2_test_label = self.create_label("ESP32H2 Test")
        self.esp32h2_test_group = self.create_group_box(self.esp32h2_test_label, "esp32h2_test")
        
        self.start_button = self.create_start_button()

        # Set up the layout
        main_layout = QVBoxLayout()
        
        # Create layouts for each section
        flash_port_layout = self.create_section_layout(self.flash_port_label, self.flash_port_combo_box, self.flash_baud_rate_label, self.flash_baud_rate_combo_box)
        factory_port_layout = self.create_section_layout(self.factory_port_label, self.factory_port_combo_box, self.factory_baud_rate_label, self.factory_baud_rate_combo_box)
        h2_flash_port_layout = self.create_section_layout(self.h2_flash_port_label, self.h2_flash_port_combo_box, self.h2_flash_baud_rate_label, self.h2_flash_baud_rate_combo_box)
        order_id_layout = self.create_section_layout(self.order_id_label, self.order_id_combo_box, None, None)
        
        # Add layouts for each section
        main_layout.addLayout(flash_port_layout)
        main_layout.addLayout(factory_port_layout)
        main_layout.addLayout(h2_flash_port_layout)
        main_layout.addLayout(order_id_layout)
        
        # Create a horizontal layout for Semi Auto Test and Manual Test
        test_group_layout = QHBoxLayout()
        test_group_layout.addWidget(self.semi_auto_test_group)
        test_group_layout.addWidget(self.manual_test_group)
        test_group_layout.addWidget(self.wifi_test_group)
        test_group_layout.addWidget(self.esp32h2_test_group)
        
        # Add test group layout
        main_layout.addLayout(test_group_layout)

        # Add start button
        main_layout.addStretch()  # Add stretchable space to absorb extra space
        main_layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)  # Center the Start button

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.select_ports_automatically()  # Automatically select ports on initialization
        self.create_menu_bar()  # Create the menu bar

    def create_menu_bar(self):
        """Creates and sets up the menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        
        # Create actions
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        esptool_action = QAction("Check esptool", self)
        esptool_action.triggered.connect(self.check_esptool)
        file_menu.addAction(esptool_action)
        
        # Use a lambda to delay the execution of process_device_data
        load_device_data_action = QAction("Load Device Data", self)
        load_device_data_action.triggered.connect(lambda: self.utils.process_device_data('device_data.txt'))
        file_menu.addAction(load_device_data_action)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        # Create actions
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_label(self, text, font_size=10, bold=False):
        """Creates and returns a label with the given text and font style."""
        label = QLabel(text, self)
        font = QFont()
        font.setPointSize(font_size)
        if bold:
            font.setBold(True)
        label.setFont(font)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Make labels fixed size
        return label

    def create_combo_box(self, items):
        """Creates and returns a combo box with the given items."""
        combo_box = QComboBox(self)
        combo_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)  # Make combo boxes fixed vertically
        combo_box.addItems(items)
        return combo_box

    def create_baud_rate_combo_box(self):
        """Creates and returns a baud rate combo box."""
        combo_box = QComboBox(self)
        combo_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)  # Make combo boxes fixed vertically
        combo_box.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        return combo_box

    def create_section_layout(self, label1, widget1, label2, widget2):
        """Creates and returns a horizontal layout for various widgets."""
        layout = QHBoxLayout()
        if label1 and widget1 or label1:
            layout.addWidget(label1)
            layout.addWidget(widget1)
        if label2 and widget2:
            layout.addWidget(label2)
            layout.addWidget(widget2)
        layout.addStretch()  # Add stretchable space at the end of each row
        return layout

    def create_group_box(self, title_label, group_type):
        """Creates and returns a QGroupBox for the specified section."""
        group_box = QGroupBox(title_label.text(), self)
        layout = QVBoxLayout()

        if group_type == "semi_auto_test":
            # Add widgets or layout specific to Semi Auto Test
            layout.addWidget(QLabel("Placeholder for Semi Auto Test", self))  # Example placeholder
            
            # ESP32-S3 Mac Address
            self.esp32s3_mac_address_label = QLabel("ESP32-S3 Mac Address:")
            self.esp32s3_mac_address_result = QLabel("<pending>")  # Pass/Fail indicator
            mac_address_layout_s3 = QHBoxLayout()
            mac_address_layout_s3.addWidget(self.esp32s3_mac_address_label)
            mac_address_layout_s3.addWidget(self.esp32s3_mac_address_result)
            layout.addLayout(mac_address_layout_s3)
            
            # ESP32-H2 Mac Address
            self.esp32h2_mac_address_label = QLabel("ESP32-H2 Mac Address:")
            self.esp32h2_mac_address_result = QLabel("<pending>")  # Pass/Fail indicator
            mac_address_layout_h2 = QHBoxLayout()
            mac_address_layout_h2.addWidget(self.esp32h2_mac_address_label)
            mac_address_layout_h2.addWidget(self.esp32h2_mac_address_result)
            layout.addLayout(mac_address_layout_h2)
            
            # ESP32-S3 Certificate Flash
            self.esp32s3_certificate_flash_label = QLabel("ESP32-S3 Certificate Flash:")
            self.esp32s3_certificate_flash_result = QLabel("<pending>")  # Pass/Fail indicator
            certificate_flash_layout_s3 = QHBoxLayout()
            certificate_flash_layout_s3.addWidget(self.esp32s3_certificate_flash_label)
            certificate_flash_layout_s3.addWidget(self.esp32s3_certificate_flash_result)
            layout.addLayout(certificate_flash_layout_s3)
            
            # ESP32-S3 Firmware Flash
            self.esp32s3_firmware_flash_label = QLabel("ESP32-S3 Firmware Flash:")
            self.esp32s3_firmware_flash_result = QLabel("<pending>")  # Pass/Fail indicator
            firmware_flash_layout_s3 = QHBoxLayout()
            firmware_flash_layout_s3.addWidget(self.esp32s3_firmware_flash_label)
            firmware_flash_layout_s3.addWidget(self.esp32s3_firmware_flash_result)
            layout.addLayout(firmware_flash_layout_s3)
            
            # ESP32-H2 Firmware Flash
            self.esp32h2_firmware_flash_label = QLabel("ESP32-H2 Firmware Flash:")
            self.esp32h2_firmware_flash_result = QLabel("<pending>")  # Pass/Fail indicator
            firmware_flash_layout_h2 = QHBoxLayout()
            firmware_flash_layout_h2.addWidget(self.esp32h2_firmware_flash_label)
            firmware_flash_layout_h2.addWidget(self.esp32h2_firmware_flash_result)
            layout.addLayout(firmware_flash_layout_h2)    
            
            # ESP32-S3 Factory Mode
            self.esp32s3_factory_mode_label = QLabel("ESP32-S3 Factory Mode:")
            self.esp32s3_factory_mode_result = QLabel("<pending>")  # Pass/Fail indicator
            factory_mode_layout_s3 = QHBoxLayout()
            factory_mode_layout_s3.addWidget(self.esp32s3_factory_mode_label)
            factory_mode_layout_s3.addWidget(self.esp32s3_factory_mode_result)
            layout.addLayout(factory_mode_layout_s3)
            
            # ESP32-S3 Read Mac Address
            self.esp32s3_read_mac_address_label = QLabel("ESP32-S3 Read Mac Address:")
            self.esp32s3_read_mac_address_result = QLabel("<pending>")  # Mac address result
            read_mac_address_layout_s3 = QHBoxLayout()
            read_mac_address_layout_s3.addWidget(self.esp32s3_read_mac_address_label)
            read_mac_address_layout_s3.addWidget(self.esp32s3_read_mac_address_result)
            layout.addLayout(read_mac_address_layout_s3)
            
            # ESP32-S3 Read Product Name
            self.esp32s3_read_product_name_label = QLabel("ESP32-S3 Read Product Name:")
            self.esp32s3_read_product_name_result = QLabel("<pending>")  # Product name result
            read_product_name_layout_s3 = QHBoxLayout()
            read_product_name_layout_s3.addWidget(self.esp32s3_read_product_name_label)
            read_product_name_layout_s3.addWidget(self.esp32s3_read_product_name_result)
            layout.addLayout(read_product_name_layout_s3)
            
            # ESP32-S3 Write Serial Number
            self.esp32s3_write_serial_number_label = QLabel("ESP32-S3 Write Serial Number:")
            self.esp32s3_write_serial_number_result = QLabel("<pending>")  # Serial number result
            write_serial_number_layout_s3 = QHBoxLayout()
            write_serial_number_layout_s3.addWidget(self.esp32s3_write_serial_number_label)
            write_serial_number_layout_s3.addWidget(self.esp32s3_write_serial_number_result)
            layout.addLayout(write_serial_number_layout_s3)
            
            # ESP32-S3 Write Matter QR
            self.esp32s3_write_matter_qr_label = QLabel("ESP32-S3 Write Matter QR:")
            self.esp32s3_write_matter_qr_result = QLabel("<pending>")  # Matter QR result
            write_matter_qr_layout_s3 = QHBoxLayout()
            write_matter_qr_layout_s3.addWidget(self.esp32s3_write_matter_qr_label)
            write_matter_qr_layout_s3.addWidget(self.esp32s3_write_matter_qr_result)
            layout.addLayout(write_matter_qr_layout_s3)
            
            # ESP32-S3 Save Device Data
            self.esp32s3_save_device_data_label = QLabel("ESP32-S3 Save Device Data:")
            self.esp32s3_save_device_data_result = QLabel("<pending>")  # Save device data result
            save_device_data_layout_s3 = QHBoxLayout()
            save_device_data_layout_s3.addWidget(self.esp32s3_save_device_data_label)
            save_device_data_layout_s3.addWidget(self.esp32s3_save_device_data_result)
            layout.addLayout(save_device_data_layout_s3)
            
        elif group_type == "manual_test":
            # Add widgets or layout specific to Manual Test
            layout.addWidget(QLabel("Placeholder for Manual Test", self))  # Example placeholder
        elif group_type == "wifi_test":
            # Add widgets or layout specific to Wi-Fi Test
            layout.addWidget(QLabel("Placeholder for Wi-Fi Test", self))
        elif group_type == "esp32h2_test":
            # Add widgets or layout specific to ESP32H2 Test
            layout.addWidget(QLabel("Placeholder for ESP32H2 Test", self))
        group_box.setLayout(layout)
        return group_box

    def create_start_button(self):
        """Creates and returns the start button."""
        button = QPushButton("Start", self)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Keep the button fixed size
        button.clicked.connect(self.start_flash)
        return button

    def start_flash(self):
        """Stores and prints the selected ports, baud rates, and order ID."""
        s3_flash_port = self.flash_port_combo_box.currentText()
        flash_baud_rate = self.flash_baud_rate_combo_box.currentText()
        factory_port = self.factory_port_combo_box.currentText()
        factory_baud_rate = self.factory_baud_rate_combo_box.currentText()
        h2_flash_port = self.h2_flash_port_combo_box.currentText()
        h2_flash_baud_rate = self.h2_flash_baud_rate_combo_box.currentText()
        order_id = self.order_id_combo_box.currentText()
        
        print(self.utils.tool_path)
        print(f"Port Flash ESP32S3: {self.utils.port_flashS3}")
        print(f"Start Address ESP32S3: {self.utils.address_start_erase_flashS3}")
        print(f"End Address ESP32S3: {self.utils.address_end_erase_flashS3}")
        print(f"Bootloader Address ESP32S3: {self.utils.address_bootloader_flashS3}")
        print(f"Partition Table Address ESP32S3: {self.utils.address_partition_table_flashS3}")
        print(f"OTA Data Initial Address ESP32S3: {self.utils.address_ota_data_initial_flashS3}")
        print(f"Firmware Address ESP32S3: {self.utils.address_firmware_flashS3}")
        print(f"Secure Cert Partition Address ESP32S3: {self.utils.address_dac_secure_cert_partition}")
        print(f"Data Provider Partition Address ESP32S3: {self.utils.address_dac_data_provider_partition}")
        print(f"Factory Port ESP32S3: {self.utils.port_factoryS3}")
        print(f"Factory Baud Rate ESP32S3: {self.utils.baud_factoryS3}")
        print("----------------")
        print(f"Port Flash ESP32H2: {self.utils.port_flashH2}")
        print(f"Start Address ESP32H2: {self.utils.address_start_erase_flashH2}")
        print(f"End Address ESP32H2: {self.utils.address_end_erase_flashH2}")
        print(f"Bootloader Address ESP32H2: {self.utils.address_bootloader_flashH2}")
        print(f"Partition Table Address ESP32H2: {self.utils.address_partition_table_flashH2}")
        print(f"Firmware Address ESP32H2: {self.utils.address_firmware_flashH2}")
        print("----------------")

        # Print the selected ports, baud rates, and order ID
        print(f"ESP32S3 Flash : {s3_flash_port} {flash_baud_rate}")
        print(f"ESP32S3 Factory : {factory_port} {factory_baud_rate}")
        print(f"ESP32H2 Flash : {h2_flash_port} {h2_flash_baud_rate}")
        print(f"Selected Order ID: {order_id}")
        
        print("----------------")
        print("Factory Command")
        print(f"Factory Command: {self.utils.command_factory_password}")
        
        self.semi_auto_test()

        
    def semi_auto_test(self):
        """Runs the semi-auto test."""
        # Semi Auto Test
        self.read_mac_address(self.utils.port_flashS3, self.utils.baud_flashS3)
        self.read_mac_address(self.utils.port_flashH2, self.utils.baud_flashH2)
        self.start_flash_s3()
        self.start_flash_h2()
        
    def read_mac_address(self, port, baud):
        """Reads the MAC address of the ESP32-S3."""
        mac_address = self.utils.esptool_read_mac(port, baud)
        if port == self.utils.port_flashS3:
            self.esp32s3_mac_address_result.setText(mac_address)
        if port == self.utils.port_flashH2:
            self.esp32h2_mac_address_result.setText(mac_address)
        else:
            pass
        
    def start_flash_s3(self):
        """Starts the semi-auto test in a separate thread."""
        self.flash_thread = FlashFirmwareS3Thread(
            self.utils.port_flashS3,
            self.utils.baud_flashS3,
            self.utils.address_bootloader_flashS3,
            self.utils.address_partition_table_flashS3,
            self.utils.address_ota_data_initial_flashS3,
            self.utils.address_firmware_flashS3,
            self.utils.address_dac_secure_cert_partition,
            self.utils.address_dac_data_provider_partition
        )
        self.flash_thread.finished.connect(self.on_flash_finished)
        self.flash_thread.start()

    def on_flash_finished(self):
        """Handles actions after the flash thread is finished."""
        print("Flash process is complete.")
        success_firmware = self.flash_thread.success_detected_firmware
        success_certificate = self.flash_thread.success_detected_certificate
        print(f"Success Firmware: {success_firmware}")
        if success_firmware:
            print("Flash firmware ESP32-S3 process was successful.")
            self.esp32s3_firmware_flash_result.setText("Pass")
        if success_certificate:
            print("Flash certificate ESP32-S3 process was successful.")
            self.esp32s3_certificate_flash_result.setText("Pass")
        self.flash_thread.quit()  # Gracefully exit the thread
        self.flash_thread.wait()  # Ensure the thread has finished execution
        
        if self.flash_thread.wait:
            print("Flash thread is finished and rebooting device.")
            self.reboot_device(self.utils.port_flashS3, self.utils.baud_flashS3)
            self.factory_mode()
            
    def factory_data_received(self, data):
        print(f"Received data: {data}")

    def on_factory_status_changed(self, status):
        print(f"Factory status changed: {status}")
        if status:  # If status is True, stop the thread
            self.esp32s3_factory_mode_result.setText("Pass")
            self.stop_thread()
        else:
            self.esp32s3_factory_mode_result.setText("Fail")

    def factory_mode(self):
        self.serial_thread = SerialReaderThread(self.utils.port_factoryS3, self.utils.baud_factoryS3)
        self.serial_thread.data_received.connect(self.factory_data_received)
        self.serial_thread.factory_status_changed.connect(self.on_factory_status_changed)
        self.serial_thread.start()

    def stop_thread(self):
        if self.serial_thread:
            print("Stopping the factory thread.")
            self.serial_thread.stop()
            self.serial_thread.quit()
            self.serial_thread.wait()  # Wait for the thread to finish
        else:
            print("No factory thread to stop.")

    def start_flash_h2(self):
        """Starts the ESP32H2 firmware flashing process in a separate thread."""
        self.flash_h2_thread = FlashFirmwareH2Thread(
            self.utils.port_flashH2,
            self.utils.baud_flashH2,
            self.utils.command_flashH2,
            self.utils.address_bootloader_flashH2,
            self.utils.address_partition_table_flashH2,
            self.utils.address_firmware_flashH2
        )
        self.flash_h2_thread.finished.connect(self.on_flash_h2_finished)
        self.flash_h2_thread.start()
        
    def on_flash_h2_finished(self):
        """Handles actions after the ESP32H2 firmware flashing thread is finished."""
        print("ESP32H2 firmware flashing process is complete.")
        success = self.flash_h2_thread.success_detected
        if success:
            print("ESP32H2 firmware flashing was successful.")
            self.esp32h2_firmware_flash_result.setText("Pass")
        else:
            print("ESP32H2 firmware flashing failed.")
            self.esp32h2_firmware_flash_result.setText("Fail")
        self.flash_h2_thread.quit()
        self.flash_h2_thread.wait()
        
    def reboot_device(self, port, baud):
        """Reboots the device using esptool."""
        self.utils.esptool_reboot(port, baud)
        
    def display_message(self, title, message):
        """Displays a message box."""
        QMessageBox.information(
            self,
            title,
            message,
            QMessageBox.StandardButton.Ok
        )

    def print_selected_order_id(self):
        """Prints the currently selected Order ID."""
        selected_order_id = self.order_id_combo_box.currentText()
        print(f"Selected Order ID: {selected_order_id}")

    def check_esptool(self):
        """Checks the functionality of esptool and shows a message box."""
        if not self.utils.check_functionality():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("esptool is not functioning correctly.")
            msg.setWindowTitle("Error")
            msg.exec()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("esptool is functioning correctly.")
            msg.setWindowTitle("Success")
            msg.exec()
            
    def show_about(self):
        """Shows the About dialog."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("Serial Port Selector v1.0\n\nCreated with PyQt6.")
        msg.setWindowTitle("About")
        msg.exec()

    def select_ports_automatically(self):
        """Automatically selects the ports based on detected devices."""
        ports = self.serialcom.get_serial_ports_as_str()
        
        # Update the combo boxes based on detected ports
        if '/dev/ttyUSB0' in ports:
            self.flash_port_combo_box.setCurrentText('/dev/ttyUSB0')
            self.flash_baud_rate_combo_box.setCurrentText('460800')
        if '/dev/ttyUSB1' in ports:
            self.factory_port_combo_box.setCurrentText('/dev/ttyUSB1')
            self.factory_baud_rate_combo_box.setCurrentText('115200')
        if '/dev/ttyUSB2' in ports:
            self.h2_flash_port_combo_box.setCurrentText('/dev/ttyUSB2')
            self.h2_flash_baud_rate_combo_box.setCurrentText('921600')
            
