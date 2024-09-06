import sys
from PyQt6.QtWidgets import QApplication
from components.gui.gui import SerialPortSelector

def main():
    app = QApplication(sys.argv)
    window = SerialPortSelector()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
