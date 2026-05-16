from data.register_config import RegisterConfigManager
import json

# 1. 创建用户的JSON文件
json_data = {
   "0": {"address": 0, "name": "温度", "scale": 0.1, "offset": 0.0, "unit": "°", "data_type": "int16", "enabled": True},
   "1": {"address": 1, "name": "压力", "scale": 1.0, "offset": 0.0, "unit": "", "data_type": "int16", "enabled": None},
   "2": {"address": 2, "name": "Reg 2", "scale": 1.0, "offset": 0.0, "unit": "", "data_type": "int16", "enabled": None},
   "3": {"address": 3, "name": "Reg 3", "scale": 1.0, "offset": 0.0, "unit": "", "data_type": "int16", "enabled": None}
}

with open('user_config.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=2)

# 2. 模拟UI中的流程
print('=== 模拟UI流程 ===')
manager = RegisterConfigManager()

# 模拟点击"加载配置"
print('1. 点击加载配置...')
success = manager.load_from_file('user_config.json')
print(f'   加载成功: {success}')
print(f'   manager中的配置数量: {manager.get_config_count()}')

# 模拟 _load_current_config
print('\n2. 调用 _load_current_config...')
configs = manager.get_all_configs()
print(f'   configs字典的长度: {len(configs)}')
print(f'   configs的类型: {type(configs)}')

print('\n3. 遍历configs...')
for address, config in configs.items():
    print(f'   地址{address}: {config.name}, enabled={config.enabled}')

# 模拟表格行数
print(f'\n4. 预期表格行数: {len(configs)}')

import os
os.remove('user_config.json')
