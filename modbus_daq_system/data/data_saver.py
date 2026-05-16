from typing import List, Dict, Optional, Callable
import pandas as pd
from datetime import datetime
import os
import threading


class DataSaver:
    def __init__(self):
        self._save_thread: Optional[threading.Thread] = None
        self._stop_save = threading.Event()
        self._is_saving = False
        self._save_interval = 1000
        self._data_provider: Optional[Callable] = None
        self._output_format = 'csv'
        self._file_path = ''
        self._save_converted = True

    def set_data_provider(self, provider):
        self._data_provider = provider

    def set_output_format(self, format_type: str):
        if format_type.lower() in ['csv', 'excel', 'xlsx']:
            self._output_format = 'xlsx' if format_type.lower() in ['excel', 'xlsx'] else 'csv'

    def set_save_interval(self, interval: int):
        self._save_interval = max(100, interval)

    def set_save_path(self, path: str):
        self._file_path = path

    def set_format(self, format_type: str):
        self.set_output_format(format_type)

    def set_save_converted(self, converted: bool):
        self._save_converted = converted

    def generate_filename(self, prefix: str = 'modbus_data') -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = '.xlsx' if self._output_format == 'xlsx' else '.csv'
        return f'{prefix}_{timestamp}{ext}'

    def save_to_csv(self, data: List[Dict], file_path: str) -> bool:
        try:
            if not data:
                return False

            df = pd.DataFrame(data)

            os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)

            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"Save to CSV error: {e}")
            return False

    def save_to_excel(self, data: List[Dict], file_path: str) -> bool:
        try:
            if not data:
                return False

            df = pd.DataFrame(data)

            os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')

            return True
        except Exception as e:
            print(f"Save to Excel error: {e}")
            return False

    def save_data(self, data: List[Dict], file_path: str) -> bool:
        if self._output_format == 'xlsx':
            return self.save_to_excel(data, file_path)
        else:
            return self.save_to_csv(data, file_path)

    def start_saving(self, data_manager):
        self._is_saving = True
        self._stop_save.clear()

        def save_loop():
            while not self._stop_save.is_set():
                self._stop_save.wait(self._save_interval / 1000.0)

                if self._stop_save.is_set():
                    break

                if data_manager:
                    data = data_manager.get_data_for_saving(converted=self._save_converted)
                    if data:
                        self.save_data(data, self._file_path)

        self._save_thread = threading.Thread(target=save_loop, daemon=True)
        self._save_thread.start()

    def stop_saving(self):
        self._stop_save.set()
        self._is_saving = False
        if self._save_thread:
            self._save_thread.join(timeout=2)

    def is_saving(self) -> bool:
        return self._is_saving
