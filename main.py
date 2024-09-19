import sys
import logging
from PyQt6.QtWidgets import QApplication
from components.gui.gui import SerialPortSelector

def main():
    app = QApplication(sys.argv)
    window = SerialPortSelector()
    window.show()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
        handlers=[
            # logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
