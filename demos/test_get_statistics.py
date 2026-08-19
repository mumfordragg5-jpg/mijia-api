import json
import time
from pathlib import Path

from mijiaAPI import mijiaAPI


# 数据目录位于项目根目录（demos 的上一级），用绝对路径避免受运行目录影响
DATA_DIR = Path(__file__).resolve().parent.parent / ".mijia-api-data"

api = mijiaAPI(DATA_DIR / "auth.json")
devices = api.get_devices_list()
for device in devices:
    if device['model'] == 'lumi.acpartner.mcn04':
        did = device['did']
        break

# 参考 https://iot.mi.com/new/doc/accesses/direct-access/extension-development/extension-functions/statistical-interface
ret = api.get_statistics({
    "did": did,
    "key": "7.1",                 # siid.piid，这里的7.1表示 lumi.acpartner.mcn04 的 power-consumption
    "data_type": "stat_month_v3", # 按月统计，可选：时（stat_hour_v3）、天（stat_day_v3）、星期（stat_week_v3）、月（stat_month_v3）
    "limit": 6,                   # 返回的最大条目数
    "time_start": int(time.time() - 24 * 3600 * 30 * 6),
    "time_end": int(time.time()),
})

"""
已知问题：
支持的设备有限，而且我的空调貌似也只支持 stat_month_v3。
比较旧的设备使用的API会不一样，需要将`data_type`中的`_v3`去掉。
并且`key`也不一样，比如 lumi.acpartner.mcn02 的统计耗电量的`key`为`powerCost`。
详见 https://github.com/Do1e/mijia-api/issues/46
"""

for item in ret:
    value = json.loads(item['value'])[0]
    ts = item['time']
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
    print(f'{date}: {value}')
