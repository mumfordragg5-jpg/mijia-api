import logging
from pathlib import Path

from mijiaAPI import mijiaAPI


logging.getLogger("mijiaAPI").setLevel(logging.DEBUG)

# 数据目录位于项目根目录（demos 的上一级），用绝对路径避免受运行目录影响
DATA_DIR = Path(__file__).resolve().parent.parent / ".mijia-api-data"

api = mijiaAPI(DATA_DIR / "auth.json")
print(api.available)
api.login() # 实际就是调用 QRlogin 方法
print(api.available)
print("Homes List:")
print(api.get_homes_list())
