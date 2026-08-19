from pathlib import Path

from mijiaAPI import mijiaAPI

# 数据目录位于项目根目录（demos 的上一级），用绝对路径避免受运行目录影响
DATA_DIR = Path(__file__).resolve().parent.parent / ".mijia-api-data"

# 【修改点1】传入你登录时保存的 auth.json 路径
# 如果是通过多租户 API 登录的，路径类似 ".mijia-api-data/sessions/user_233-111.json"
# 如果是你之前用老版本默认登录的，路径可能是 "~/.config/mijia-api/auth.json" (可以填 None 自动识别老路径)
auth_path = DATA_DIR / "sessions/user_22345.json"
api = mijiaAPI(auth_data_path=auth_path)

# 【修改点2】注释掉 login，因为已经登录过了，直接使用缓存的凭证
# api.login()

if not api.available:
    print("凭证已失效或不存在，请重新登录！")
    exit(1)

# 获取所有家庭
homes = api.get_homes_list()
print("=== 家庭列表 ===")
print(homes)
print("\n")

if len(homes) > 0:
    # 获取所有设备（不包含共享设备）
    devices = api.get_devices_list()
    print("=== 全部设备列表 ===")
    for device in devices:
        print(f"设备名称: {device['name']}, Model: {device['model']}, Did: {device['did']}")
    print("\n")

    # 获取指定家庭的设备
    home_id = homes[0]['id']
    devices_in_home = api.get_devices_list(home_id=home_id)
    print(f"=== [{homes[0]['name']}] 家庭的设备 ===")
    for device in devices_in_home:
        print(f"设备名称: {device['name']}, Model: {device['model']}, Did: {device['did']}")
    print("\n")

# 获取共享设备列表（无法指定家庭ID）
shared_devices = api.get_shared_devices_list()
print("=== 共享设备列表 ===")
for device in shared_devices:
    print(f"共享设备名称: {device['name']}, Model: {device['model']}, Did: {device['did']}")

# 获取设备属性（原始 siid/piid 方式）
result = api.get_devices_prop({
    "did": "918180841",
    "siid": 2,
    "piid": 4
})
print("=== 获取设备属性 ===")
print(result)

# 设置设备属性（原始 siid/piid 方式）
# result = api.set_devices_prop([{
#     "did": "918180841",
#     "siid": 2,
#     "piid": 5,    # 对应你截图里的 #5 设定温度
#     "value": 50   # 直接设定为你想要的温度
# }])
# print("=== 设置设备属性 ===")
# print(result)

## 执行烧水动作
result = api.run_action({
    "did": "918180841",
    "siid": 2,
    "aiid": 1,
    "in": [
        "M0",    # piid: 17，现在的正确姿势
        50,      # piid: 5，目标温度
        True,    # piid: 7，开启自动保温
        55,      # piid: 8，保温温度
        True,    # piid: 10，开启除氯
        False,   # piid: 12，不快冷
        55,      # piid: 13，纯净水保温
        41       # piid: 14，自来水保温
    ]
})
print("执行开始烧水动作:", result)

result2 = api.get_devices_prop([
    {"did": "918180841", "siid": 2, "piid": 17},
    {"did": "918180841", "siid": 2, "piid": 5},
    {"did": "918180841", "siid": 2, "piid": 7},
    {"did": "918180841", "siid": 2, "piid": 8},
    {"did": "918180841", "siid": 2, "piid": 10},
    {"did": "918180841", "siid": 2, "piid": 12},
    {"did": "918180841", "siid": 2, "piid": 13},
    {"did": "918180841", "siid": 2, "piid": 14}
])
print("=== 获取设备属性 ===")
print(result2)

#
# # 执行设备动作（如开关灯的切换动作）
# result2 = api.run_action({
#     "did": "918180841",
#     "siid": 2,
#     "aiid": 0
# })
# print("=== 执行设备动作 ===")
# print(result2)



