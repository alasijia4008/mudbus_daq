from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from typing import Dict, List


class CurveDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._curves: Dict[int, pg.PlotDataItem] = {}
        self._colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (128, 0, 0), (0, 128, 0), (0, 0, 128)
        ]
        self._color_index = 0
        self._max_points = 500
        self._data: Dict[int, list] = {}
        self._timestamps: list = []
        self._base_time: float = 0.0
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.addLegend()

        self.plot_widget.setXRange(0, 60)
        self.plot_widget.setYRange(0, 100)

        layout.addWidget(self.plot_widget)

    def add_curve(self, address: int, label: str = None):
        if address in self._curves:
            return

        color = self._colors[self._color_index % len(self._colors)]
        self._color_index += 1

        pen = pg.mkPen(color=color, width=2)
        curve_label = label or f'Reg {address}'

        curve = self.plot_widget.plot(pen=pen, name=curve_label)
        self._curves[address] = curve
        self._data[address] = []

    def remove_curve(self, address: int):
        if address in self._curves:
            self.plot_widget.removeItem(self._curves[address])
            del self._curves[address]
            if address in self._data:
                del self._data[address]

    def clear_curves(self):
        for address in list(self._curves.keys()):
            self.remove_curve(address)

    def update_data(self, registers: List[int], start_address: int, timestamp: float):
        if not self._timestamps:
            self._base_time = timestamp

        relative_time = timestamp - self._base_time

        while len(self._timestamps) > 0 and len(self._timestamps) > self._max_points:
            self._timestamps.pop(0)
            for addr in self._data:
                if self._data[addr]:
                    self._data[addr].pop(0)

        self._timestamps.append(relative_time)

        for i, value in enumerate(registers):
            addr = start_address + i
            if addr not in self._curves:
                self.add_curve(addr)

            if addr not in self._data:
                self._data[addr] = []

            self._data[addr].append(value)

            while len(self._data[addr]) > self._max_points:
                self._data[addr].pop(0)

        self._update_plot()

    def _update_plot(self):
        for addr, curve in self._curves.items():
            if addr in self._data and len(self._data[addr]) > 0:
                x_data = self._timestamps[-len(self._data[addr]):]
                y_data = self._data[addr]
                curve.setData(x_data, y_data)

        if len(self._timestamps) > 1:
            x_range = max(self._timestamps[-1], 10)
            self.plot_widget.setXRange(max(0, x_range - 60), x_range)

    def set_max_points(self, max_points: int):
        self._max_points = max_points

    def reset(self):
        self._timestamps.clear()
        self._data.clear()
        self._base_time = 0.0
        for curve in self._curves.values():
            curve.setData([])
