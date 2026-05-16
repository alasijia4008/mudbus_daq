from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QComboBox, QSpinBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QFileDialog,
                             QMessageBox, QLineEdit, QCheckBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from ui.widgets.curve_display import CurveDisplayWidget
from ui.widgets.register_config_dialog import RegisterConfigDialog
from data.register_config import RegisterConfigManager
import threading


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.modbus_handler = None
        self.data_manager = None
        self.data_saver = None
        self.config_manager = RegisterConfigManager()
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.setWindowTitle("Modbus RTU 数据采集系统")
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QVBoxLayout()

        config_group = self._create_config_group()
        main_layout.addWidget(config_group)

        modbus_config_group = self._create_modbus_config_group()
        main_layout.addWidget(modbus_config_group)

        control_group = self._create_control_group()
        main_layout.addWidget(control_group)

        table_group = self._create_table_group()
        main_layout.addWidget(table_group)

        curve_group = self._create_curve_group()
        main_layout.addWidget(curve_group)

        save_group = self._create_save_group()
        main_layout.addWidget(save_group)

        self.setLayout(main_layout)

        self.status_label = QLabel("状态: 未连接")
        main_layout.addWidget(self.status_label)

    def _create_config_group(self):
        group = QGroupBox("通信配置")

        serial_layout = QHBoxLayout()
        serial_layout.addWidget(QLabel("串口:"))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(100)
        serial_layout.addWidget(self.port_combo)

        serial_layout.addWidget(QLabel("波特率:"))
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200'])
        self.baudrate_combo.setCurrentText('9600')
        serial_layout.addWidget(self.baudrate_combo)

        serial_layout.addWidget(QLabel("校验:"))
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(['N', 'E', 'O'])
        serial_layout.addWidget(self.parity_combo)

        serial_layout.addWidget(QLabel("数据位:"))
        self.bytesize_combo = QComboBox()
        self.bytesize_combo.addItems(['7', '8'])
        self.bytesize_combo.setCurrentText('8')
        serial_layout.addWidget(self.bytesize_combo)

        serial_layout.addWidget(QLabel("停止位:"))
        self.stopbits_combo = QComboBox()
        self.stopbits_combo.addItems(['1', '2'])
        serial_layout.addWidget(self.stopbits_combo)

        refresh_btn = QPushButton("刷新串口")
        refresh_btn.clicked.connect(self._refresh_ports)
        serial_layout.addWidget(refresh_btn)
        serial_layout.addStretch()

        group.setLayout(serial_layout)
        return group

    def _create_modbus_config_group(self):
        group = QGroupBox("Modbus配置")

        layout = QHBoxLayout()

        layout.addWidget(QLabel("从机地址:"))
        self.slave_spin = QSpinBox()
        self.slave_spin.setRange(1, 247)
        self.slave_spin.setValue(1)
        layout.addWidget(self.slave_spin)

        layout.addWidget(QLabel("起始寄存器:"))
        self.start_addr_spin = QSpinBox()
        self.start_addr_spin.setRange(0, 65535)
        self.start_addr_spin.setValue(0)
        layout.addWidget(self.start_addr_spin)

        layout.addWidget(QLabel("寄存器数量:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 125)
        self.count_spin.setValue(10)
        layout.addWidget(self.count_spin)

        layout.addWidget(QLabel("采集周期(ms):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 10000)
        self.interval_spin.setValue(1000)
        self.interval_spin.setSingleStep(100)
        layout.addWidget(self.interval_spin)

        config_btn = QPushButton("寄存器配置")
        config_btn.clicked.connect(self._open_register_config)
        layout.addWidget(config_btn)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_control_group(self):
        group = QGroupBox("控制")

        layout = QHBoxLayout()

        self.connect_btn = QPushButton("连接")
        self.connect_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        layout.addWidget(self.connect_btn)

        self.start_btn = QPushButton("开始采集")
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止采集")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        layout.addWidget(self.stop_btn)

        self.clear_btn = QPushButton("清空数据")
        layout.addWidget(self.clear_btn)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_table_group(self):
        group = QGroupBox("数据表格")

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["地址", "名称", "原始值", "物理值", "单位"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(200)

        layout.addWidget(self.table)

        group.setLayout(layout)
        return group

    def _create_curve_group(self):
        group = QGroupBox("实时曲线")

        layout = QVBoxLayout()

        self.curve_widget = CurveDisplayWidget()
        self.curve_widget.setMinimumHeight(300)

        layout.addWidget(self.curve_widget)

        group.setLayout(layout)
        return group

    def _create_save_group(self):
        group = QGroupBox("数据保存")

        layout = QHBoxLayout()

        layout.addWidget(QLabel("保存路径:"))
        self.save_path_edit = QLineEdit()
        self.save_path_edit.setPlaceholderText("选择保存路径...")
        layout.addWidget(self.save_path_edit)

        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse_save_path)
        layout.addWidget(browse_btn)

        self.format_combo = QComboBox()
        self.format_combo.addItems(['CSV', 'Excel'])
        layout.addWidget(self.format_combo)

        self.save_converted_check = QCheckBox("保存物理值")
        self.save_converted_check.setChecked(True)
        layout.addWidget(self.save_converted_check)

        self.save_btn = QPushButton("开始保存")
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")
        layout.addWidget(self.save_btn)

        self.stop_save_btn = QPushButton("停止保存")
        self.stop_save_btn.setEnabled(False)
        layout.addWidget(self.stop_save_btn)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _connect_signals(self):
        self.connect_btn.clicked.connect(self._on_connect)
        self.start_btn.clicked.connect(self._on_start_collection)
        self.stop_btn.clicked.connect(self._on_stop_collection)
        self.clear_btn.clicked.connect(self._on_clear_data)
        self.save_btn.clicked.connect(self._on_start_save)
        self.stop_save_btn.clicked.connect(self._on_stop_save)

    def initialize(self, modbus_handler, data_manager, data_saver):
        self.modbus_handler = modbus_handler
        self.data_manager = data_manager
        self.data_saver = data_saver
        self.data_manager.set_config_manager(self.config_manager)

        self._refresh_ports()

    def _refresh_ports(self):
        import serial.tools.list_ports
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo.clear()
        if ports:
            self.port_combo.addItems(ports)
        else:
            self.port_combo.addItem("无可用串口")

    def _on_connect(self):
        if self.modbus_handler.connected:
            self.modbus_handler.disconnect()
            self.connect_btn.setText("连接")
            self.connect_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
            self.start_btn.setEnabled(False)
            self.status_label.setText("状态: 未连接")
        else:
            port = self.port_combo.currentText()
            if port == "无可用串口":
                QMessageBox.warning(self, "警告", "请选择有效的串口")
                return

            baudrate = int(self.baudrate_combo.currentText())
            parity = self.parity_combo.currentText()
            bytesize = int(self.bytesize_combo.currentText())
            stopbits = int(self.stopbits_combo.currentText())

            if self.modbus_handler.connect(port, baudrate, parity, stopbits, bytesize):
                self.connect_btn.setText("断开")
                self.connect_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
                self.start_btn.setEnabled(True)
                self.status_label.setText(f"状态: 已连接 {port}")
            else:
                QMessageBox.critical(self, "错误", "连接失败")

    def _on_start_collection(self):
        slave = self.slave_spin.value()
        start_addr = self.start_addr_spin.value()
        count = self.count_spin.value()
        interval = self.interval_spin.value()

        self.data_manager.set_register_config(start_addr, count)

        self.modbus_handler.set_read_callback(self._on_data_received)
        self.modbus_handler.start_polling(start_addr, count, slave, interval)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.status_label.setText("状态: 采集中...")

    def _on_stop_collection(self):
        self.modbus_handler.stop_polling()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("状态: 已停止采集")

    def _open_register_config(self):
        dialog = RegisterConfigDialog(self.config_manager, self)
        dialog.exec_()
        self.data_manager.set_config_manager(self.config_manager)

    def _on_data_received(self, registers, timestamp):
        start_addr = self.start_addr_spin.value()
        self.data_manager.add_data(registers, timestamp)

        self._update_table(registers, start_addr)

        self._update_curve_with_converted_values(registers, start_addr, timestamp)

    def _update_curve_with_converted_values(self, registers, start_addr, timestamp):
        converted_values = []
        for i, raw_value in enumerate(registers):
            addr = start_addr + i
            converted_value = self.data_manager.get_latest_value(addr, converted=True)
            converted_values.append(int(converted_value) if converted_value is not None else raw_value)

        self.curve_widget.update_data(converted_values, start_addr, timestamp)

    def _update_table(self, registers, start_addr):
        self.table.blockSignals(True)

        for i, raw_value in enumerate(registers):
            addr = start_addr + i

            row = self._find_or_create_row(addr)

            config = self.config_manager.get_config(addr)
            name = config.name if config else f"Reg {addr}"
            unit = config.unit if config else ""

            name_item = self.table.item(row, 1)
            if not name_item or name_item.text() != name:
                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, name_item)

            raw_item = QTableWidgetItem(str(raw_value))
            raw_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, raw_item)

            converted_value = self.data_manager.get_latest_value(addr, converted=True)
            if converted_value is not None:
                converted_str = f"{converted_value:.4f}" if isinstance(converted_value, float) else str(converted_value)
            else:
                converted_str = str(raw_value)
            converted_item = QTableWidgetItem(converted_str)
            converted_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, converted_item)

            unit_item = QTableWidgetItem(unit)
            unit_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, unit_item)

        self.table.blockSignals(False)

    def _find_or_create_row(self, addr: int) -> int:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == str(addr):
                return row

        row = self.table.rowCount()
        self.table.insertRow(row)

        addr_item = QTableWidgetItem(str(addr))
        addr_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, addr_item)

        return row

    def _browse_save_path(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择保存路径", "", "CSV文件 (*.csv);;Excel文件 (*.xlsx)"
        )
        if file_path:
            self.save_path_edit.setText(file_path)

    def _on_start_save(self):
        save_path = self.save_path_edit.text()
        if not save_path:
            QMessageBox.warning(self, "警告", "请选择保存路径")
            return

        file_format = self.format_combo.currentText()
        save_converted = self.save_converted_check.isChecked()

        self.data_saver.set_save_path(save_path)
        self.data_saver.set_format(file_format)
        self.data_saver.set_save_converted(save_converted)

        self.data_saver.start_saving(self.data_manager)

        self.save_btn.setEnabled(False)
        self.stop_save_btn.setEnabled(True)
        self.status_label.setText("状态: 保存中...")

    def _on_stop_save(self):
        self.data_saver.stop_saving()

        self.save_btn.setEnabled(True)
        self.stop_save_btn.setEnabled(False)
        self.status_label.setText("状态: 已停止保存")

    def _on_clear_data(self):
        self.data_manager.clear()
        self.table.setRowCount(0)
        self.curve_widget.reset()
        self.status_label.setText("状态: 数据已清空")
