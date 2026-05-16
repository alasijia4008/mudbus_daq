from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QDialog, QLabel, QLineEdit, QComboBox,
                             QMessageBox, QFileDialog, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from typing import List, Dict
from data.register_config import RegisterConfigManager, RegisterConfig


class RegisterConfigDialog(QDialog):
    def __init__(self, config_manager: RegisterConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self._init_ui()
        self._load_current_config()

    def _init_ui(self):
        self.setWindowTitle("寄存器配置")
        self.setGeometry(200, 200, 700, 500)

        layout = QVBoxLayout()

        info_label = QLabel("配置各寄存器的比例(Scale)和偏移(Offset)以获取真实物理量\n公式: 真实值 = 原始值 × 比例 + 偏移")
        layout.addWidget(info_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['地址', '名称', '比例(Scale)', '偏移(Offset)', '单位', '启用'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("添加配置")
        self.add_btn.clicked.connect(self._add_config)
        button_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton("删除选中")
        self.remove_btn.clicked.connect(self._remove_selected)
        button_layout.addWidget(self.remove_btn)

        self.load_btn = QPushButton("加载配置")
        self.load_btn.clicked.connect(self._load_config)
        button_layout.addWidget(self.load_btn)

        self.save_btn = QPushButton("保存配置")
        self.save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(self.save_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        ok_layout = QHBoxLayout()
        ok_layout.addStretch()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self._on_ok)
        ok_layout.addWidget(ok_btn)

        layout.addLayout(ok_layout)

        self.setLayout(layout)

    def _load_current_config(self):
        self.table.setRowCount(0)
        configs = self.config_manager.get_all_configs()
        
        for address, config in configs.items():
            self._add_table_row(config)

    def _add_table_row(self, config: RegisterConfig):
        row = self.table.rowCount()
        self.table.insertRow(row)

        addr_item = QTableWidgetItem(str(config.address))
        addr_item.setFlags(addr_item.flags() & ~Qt.ItemIsEditable)
        addr_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, addr_item)

        name_item = QTableWidgetItem(config.name)
        self.table.setItem(row, 1, name_item)

        scale_item = QTableWidgetItem(str(config.scale))
        scale_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, scale_item)

        offset_item = QTableWidgetItem(str(config.offset))
        offset_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, offset_item)

        unit_item = QTableWidgetItem(config.unit)
        unit_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 4, unit_item)

        enable_item = QTableWidgetItem("是" if config.enabled else "否")
        enable_item.setTextAlignment(Qt.AlignCenter)
        if config.enabled:
            enable_item.setBackground(QColor(144, 238, 144))
        else:
            enable_item.setBackground(QColor(255, 182, 193))
        self.table.setItem(row, 5, enable_item)

    def _add_config(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        base_addr = 0
        existing_addrs = set()
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item:
                try:
                    existing_addrs.add(int(item.text()))
                except:
                    pass

        while base_addr in existing_addrs:
            base_addr += 1

        addr_item = QTableWidgetItem(str(base_addr))
        addr_item.setFlags(addr_item.flags() & ~Qt.ItemIsEditable)
        addr_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, addr_item)

        name_item = QTableWidgetItem(f"Reg {base_addr}")
        name_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, name_item)

        scale_item = QTableWidgetItem("1.0")
        scale_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, scale_item)

        offset_item = QTableWidgetItem("0.0")
        offset_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, offset_item)

        unit_item = QTableWidgetItem("")
        unit_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 4, unit_item)

        enable_item = QTableWidgetItem("是")
        enable_item.setTextAlignment(Qt.AlignCenter)
        enable_item.setBackground(QColor(144, 238, 144))
        self.table.setItem(row, 5, enable_item)

    def _remove_selected(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def _save_config(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置", "", "JSON Files (*.json)"
        )
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'

            if self._apply_config_to_manager():
                self.config_manager.save_to_file(file_path)
                QMessageBox.information(self, "成功", f"配置已保存到:\n{file_path}")

    def _load_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载配置", "", "JSON Files (*.json)"
        )
        if file_path:
            if self.config_manager.load_from_file(file_path):
                self._load_current_config()
                QMessageBox.information(self, "成功", "配置已加载")
            else:
                QMessageBox.warning(self, "错误", "加载配置失败")

    def _apply_config_to_manager(self) -> bool:
        temp_configs = {}

        for row in range(self.table.rowCount()):
            try:
                addr_item = self.table.item(row, 0)
                name_item = self.table.item(row, 1)
                scale_item = self.table.item(row, 2)
                offset_item = self.table.item(row, 3)
                unit_item = self.table.item(row, 4)
                enable_item = self.table.item(row, 5)

                if not addr_item:
                    continue
                
                address = int(addr_item.text())
                    
                # 其他字段可以为空，使用默认值
                if not name_item or not name_item.text():
                    name = f"Reg {address}"
                else:
                    name = name_item.text()

                if not scale_item or not scale_item.text():
                    scale = 1.0
                else:
                    scale = float(scale_item.text())

                if not offset_item or not offset_item.text():
                    offset = 0.0
                else:
                    offset = float(offset_item.text())

                unit = unit_item.text() if unit_item and unit_item.text() else ""
                enabled = enable_item and enable_item.text() == "是"

                config = RegisterConfig(address)
                config.name = name
                config.scale = scale
                config.offset = offset
                config.unit = unit
                config.enabled = enabled
                temp_configs[address] = config
            except (ValueError, AttributeError) as e:
                QMessageBox.warning(self, "数据错误", f"第{row+1}行数据格式错误: {e}")
                return False

        self.config_manager.clear()
        for addr, config in temp_configs.items():
            self.config_manager.add_config(config)

        return True

    def _on_ok(self):
        if self._apply_config_to_manager():
            self.accept()

    def get_config_manager(self) -> RegisterConfigManager:
        return self.config_manager
