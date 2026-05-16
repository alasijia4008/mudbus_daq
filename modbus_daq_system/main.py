import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from communication.modbus_handler import ModbusHandler
from data.data_manager import DataManager
from data.data_saver import DataSaver


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    modbus_handler = ModbusHandler()
    data_manager = DataManager(max_history=1000)
    data_saver = DataSaver()

    window = MainWindow()
    window.initialize(modbus_handler, data_manager, data_saver)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
