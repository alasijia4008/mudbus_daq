from typing import Dict, List, Optional, Any
from collections import deque
from datetime import datetime
import threading


class DataManager:
    def __init__(self, max_history: int = 1000):
        self._data: Dict[int, deque] = {}
        self._timestamps: deque = deque(maxlen=max_history)
        self._lock = threading.Lock()
        self.max_history = max_history
        self._register_count: int = 0
        self._start_address: int = 0
        self._config_manager = None

    def set_config_manager(self, config_manager):
        self._config_manager = config_manager

    def set_register_config(self, start_address: int, count: int):
        self._start_address = start_address
        self._register_count = count
        with self._lock:
            for i in range(count):
                reg_addr = start_address + i
                if reg_addr not in self._data:
                    self._data[reg_addr] = deque(maxlen=self.max_history)

    def _convert_value(self, address: int, raw_value: int) -> float:
        if self._config_manager:
            return self._config_manager.apply_conversion(address, raw_value)
        return float(raw_value)

    def add_data(self, registers: List[int], timestamp: float):
        with self._lock:
            self._timestamps.append(timestamp)

            for i, value in enumerate(registers):
                reg_addr = self._start_address + i
                if reg_addr not in self._data:
                    self._data[reg_addr] = deque(maxlen=self.max_history)
                self._data[reg_addr].append(value)

    def get_latest_value(self, address: int, converted: bool = False) -> Optional[Any]:
        with self._lock:
            if address in self._data and len(self._data[address]) > 0:
                raw_value = self._data[address][-1]
                if converted:
                    return self._convert_value(address, raw_value)
                return raw_value
            return None

    def get_latest_values(self, converted: bool = False) -> Dict[int, Any]:
        with self._lock:
            result = {}
            for addr, values in self._data.items():
                if len(values) > 0:
                    raw_value = values[-1]
                    result[addr] = self._convert_value(addr, raw_value) if converted else raw_value
                else:
                    result[addr] = None
            return result

    def get_latest_converted_values(self) -> Dict[int, Dict[str, Any]]:
        with self._lock:
            result = {}
            for addr, values in self._data.items():
                if len(values) > 0:
                    raw_value = values[-1]
                    converted_value = self._convert_value(addr, raw_value)
                    config = self._config_manager.get_config(addr) if self._config_manager else None
                    unit = config.unit if config else ""

                    result[addr] = {
                        'raw': raw_value,
                        'converted': converted_value,
                        'unit': unit,
                        'name': config.name if config else f"Reg {addr}"
                    }
            return result

    def get_history(self, address: int) -> List[Any]:
        with self._lock:
            if address in self._data:
                return list(self._data[address])
            return []

    def get_all_history(self) -> Dict[int, List[Any]]:
        with self._lock:
            return {
                addr: list(values)
                for addr, values in self._data.items()
            }

    def get_timestamps(self) -> List[float]:
        with self._lock:
            return list(self._timestamps)

    def get_data_for_saving(self, converted: bool = False) -> List[Dict]:
        with self._lock:
            result = []
            timestamps = list(self._timestamps)

            for i, ts in enumerate(timestamps):
                row = {'timestamp': datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}

                for addr, values in self._data.items():
                    if i < len(values):
                        if converted:
                            row[str(addr)] = self._convert_value(addr, values[i])
                        else:
                            row[str(addr)] = values[i]

                result.append(row)

            return result

    def get_register_count(self) -> int:
        return self._register_count

    def get_start_address(self) -> int:
        return self._start_address

    def clear(self):
        with self._lock:
            self._data.clear()
            self._timestamps.clear()

    def get_data_count(self) -> int:
        with self._lock:
            return len(self._timestamps)
