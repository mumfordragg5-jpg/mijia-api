import logging
from pathlib import Path

from mijiaAPI import mijiaAPI, mijiaDevice


logging.getLogger("mijiaAPI").setLevel(logging.WARNING)

# 数据目录位于项目根目录（demos 的上一级），用绝对路径避免受运行目录影响
DATA_DIR = Path(__file__).resolve().parent.parent / ".mijia-api-data"

api = mijiaAPI(DATA_DIR / "auth.json")
devices = api.get_devices_list()
for device in devices:
    if device['model'] == 'yeelink.light.lamp4':
        did = device['did']
        break

# sleep_time 是可选的，默认是 0.5
# 设置后获取属性值时需要等待一段时间，否则可能获取到不正确的
device = mijiaDevice(api, did, sleep_time=1)
print(device)
print("---------------------")
print(f"on: {device.get('on')}")
device.set('on', True)
print("---------------------")
print(f"{device.get('brightness')}")
device.set('brightness', 60)
print(f"{device.get('brightness')}")
print("---------------------")
print(f"{device.get('color-temperature')}")
device.set('color-temperature', 5000)
print(f"{device.get('color-temperature')}")
print("---------------------")
device.set('mode', 0)
print(f"{device.get('brightness')}")
print(f"{device.get('color-temperature')}")
print("---------------------")
print(f"{device.get('brightness')}")
device.set('brightness-delta', -10)
print(f"{device.get('brightness')}")
print("---------------------")
print(f"{device.get('color-temperature')}")
device.set('ct-delta', -10)
print(f"{device.get('color-temperature')}")
device.set('ct-adjust-alexa', 1) # increase
print(f"{device.get('color-temperature')}")
device.set('ct-adjust-alexa', 2) # decrease
print(f"{device.get('color-temperature')}")
print("---------------------")
device.run_action('toggle')
print(f"on: {device.get('on')}")
