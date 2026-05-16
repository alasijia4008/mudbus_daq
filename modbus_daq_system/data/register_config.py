from typing import Dict, Optional
import json
import os


class RegisterConfig:
    def __init__(self, address: int):
        self.address = address
        self.name: str = f"Reg {address}"
        self.scale: float = 1.0
        self.offset: float = 0.0
        self.unit: str = ""
        self.data_type: str = "int16"
        self.enabled: bool = True

    def to_dict(self) -> dict:
        return {
            'address': self.address,
            'name': self.name,
            'scale': self.scale,
            'offset': self.offset,
            'unit': self.unit,
            'data_type': self.data_type,
            'enabled': self.enabled
        }

    @staticmethod
    def from_dict(data: dict) -> 'RegisterConfig':
        config = RegisterConfig(data['address'])
        config.name = data.get('name', f"Reg {data['address']}")
        config.scale = data.get('scale', 1.0)
        config.offset = data.get('offset', 0.0)
        config.unit = data.get('unit', '')
        config.data_type = data.get('data_type', 'int16')
        enabled = data.get('enabled')
        config.enabled = True if enabled is None else enabled
        return config

    def apply_conversion(self, raw_value: int) -> float:
        return raw_value * self.scale + self.offset


class RegisterConfigManager:
    def __init__(self):
        self._configs: Dict[int, RegisterConfig] = {}

    def add_config(self, config: RegisterConfig):
        self._configs[config.address] = config

    def remove_config(self, address: int):
        if address in self._configs:
            del self._configs[address]

    def get_config(self, address: int) -> Optional[RegisterConfig]:
        return self._configs.get(address)

    def get_all_configs(self) -> Dict[int, RegisterConfig]:
        return self._configs.copy()

    def update_config(self, address: int, name: str = None, scale: float = None,
                     offset: float = None, unit: str = None, data_type: str = None,
                     enabled: bool = None):
        if address not in self._configs:
            self._configs[address] = RegisterConfig(address)

        config = self._configs[address]
        if name is not None:
            config.name = name
        if scale is not None:
            config.scale = scale
        if offset is not None:
            config.offset = offset
        if unit is not None:
            config.unit = unit
        if data_type is not None:
            config.data_type = data_type
        if enabled is not None:
            config.enabled = enabled

    def apply_conversion(self, address: int, raw_value: int) -> float:
        if address in self._configs and self._configs[address].enabled:
            return self._configs[address].apply_conversion(raw_value)
        return float(raw_value)

    def save_to_file(self, file_path: str):
        data = {
            str(addr): config.to_dict()
            for addr, config in self._configs.items()
        }
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._configs.clear()
            for addr_str, config_data in data.items():
                config = RegisterConfig.from_dict(config_data)
                self._configs[config.address] = config
            return True
        except Exception as e:
            print(f"Load config error: {e}")
            return False

    def clear(self):
        self._configs.clear()

    def get_config_count(self) -> int:
        return len(self._configs)
