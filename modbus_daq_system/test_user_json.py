from data.register_config import RegisterConfigManager
import json

# 模拟用户的JSON文件内容
json_data = {
   "0": {
     "address": 0,
     "name": "温度",
     "scale": 0.1,
     "offset": 0.0,
     "unit": "°",
     "data_type": "int16",
     "enabled": True
   },
   "1": {
     "address": 1,
     "name": "压力",
     "scale": 1.0,
     "offset": 0.0,
     "unit": "",
     "data_type": "int16",
     "enabled": None  # null
   },
   "2": {
     "address": 2,
     "name": "Reg 2",
     "scale": 1.0,
     "offset": 0.0,
     "unit": "",
     "data_type": "int16",
     "enabled": None  # null
   },
   "3": {
     "address": 3,
     "name": "Reg 3",
     "scale": 1.0,
     "offset": 0.0,
     "unit": "",
     "data_type": "int16",
     "enabled": None  # null
   }
}

# 保存到文件
with open('test_user.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=2)

print('=== 测试加载用户的JSON文件 ===')
manager = RegisterConfigManager()

try:
    success = manager.load_from_file('test_user.json')
    print(f'加载结果: {success}')
    print(f'加载后配置数量: {manager.get_config_count()}')
    
    for addr, cfg in manager.get_all_configs().items():
        print(f'  地址{addr}: {cfg.name}, enabled={cfg.enabled}')
        
except Exception as e:
    print(f'加载时发生异常: {type(e).__name__}: {e}')

import os
os.remove('test_user.json')
