from data.register_config import RegisterConfigManager
import json
import os

# 1. 创建 manager 并添加配置
manager = RegisterConfigManager()
manager.update_config(0, name='温度', scale=0.1, offset=-50, unit='C', enabled=True)
manager.update_config(1, name='压力', scale=0.01, offset=0, unit='MPa', enabled=True)
manager.update_config(2, name='流量', scale=0.5, offset=10, unit='L/s', enabled=True)

print('=== 添加3个配置后的状态 ===')
print(f'Manager配置数量: {manager.get_config_count()}')
for addr, cfg in manager.get_all_configs().items():
    print(f'  {addr}: {cfg.name}')

# 2. 保存到文件
manager.save_to_file('test_full.json')
print('\n=== 保存到文件 ===')

# 3. 查看JSON文件内容
with open('test_full.json', 'r', encoding='utf-8') as f:
    saved_data = json.load(f)
    print(f'JSON文件中的配置数量: {len(saved_data)}')
    for key in saved_data:
        print(f'  Key: {key}, Name: {saved_data[key]["name"]}')

# 4. 模拟加载
manager.clear()
print(f'\n清空后Manager配置数量: {manager.get_config_count()}')

manager.load_from_file('test_full.json')
print('\n=== 从文件加载后的状态 ===')
print(f'Manager配置数量: {manager.get_config_count()}')
for addr, cfg in manager.get_all_configs().items():
    print(f'  {addr}: {cfg.name}')

os.remove('test_full.json')
print('\n测试完成!')
