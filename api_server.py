import logging
import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field

from mijiaAPI import mijiaAPI

# 设置日志级别
logging.getLogger("mijiaAPI").setLevel(logging.INFO)

app = FastAPI(title="Mijia API Service", description="A FastAPI wrapper for Mijia API to be consumed by Java")

# 定义 Pydantic 模型，用于请求体验证
class Prop(BaseModel):
    did: str
    siid: int
    piid: int
    value: Optional[Any] = None

class Action(BaseModel):
    did: str
    siid: int
    aiid: int
    in_list: Optional[List[Any]] = Field(default=None, alias="in")

class StatQuery(BaseModel):
    did: str
    key: str
    data_type: str
    limit: int
    time_start: int
    time_end: int

# 依赖注入，动态获取用户的 mijiaAPI 实例
def get_api(x_session_id: str = Header(..., description="Unique Session ID for the user (e.g. user_123)")) -> mijiaAPI:
    # 确保存储目录存在
    sessions_dir = ".mijia-api-data/sessions"
    os.makedirs(sessions_dir, exist_ok=True)
    
    auth_path = os.path.join(sessions_dir, f"{x_session_id}.json")
    return mijiaAPI(auth_path)

@app.get("/status", summary="获取 API 状态")
def get_status(api: mijiaAPI = Depends(get_api)):
    return {"available": api.available}

@app.post("/login", summary="一步登录 (终端扫码)")
def login_one_step(api: mijiaAPI = Depends(get_api)):
    """
    触发完整的登录流程。如果没有有效的认证信息，这会在运行服务端的终端里打印二维码让你扫描。
    注意：这会阻塞当前请求，直到扫码登录完成或超时。
    """
    try:
        api.login()
        return {"status": "success", "available": api.available}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login/init", summary="初始化登录获取二维码")
def login_init(api: mijiaAPI = Depends(get_api)):
    """
    初始化登录流程。如果之前已经登录且 token 有效，直接返回成功。
    否则返回包含二维码图片链接 (qr_url) 和后续所需的 login_data。
    """
    login_data = api._get_qr_login_data()
    if login_data.get("refreshed"):
        return {"status": "success", "step": "done", "message": "Already logged in"}
    return {
        "status": "success", 
        "step": "scan", 
        "qr_url": login_data["qr"], # 二维码图片链接
        "login_url": login_data["loginUrl"], # 二维码原始链接
        "login_data": login_data
    }

@app.post("/login/complete", summary="等待扫码并完成登录")
def login_complete(login_data: dict, api: mijiaAPI = Depends(get_api)):
    """
    调用此接口将长轮询等待用户扫码确认（最长阻塞约 2 分钟）。
    需要在请求体中原样传入 /login/init 接口返回的 login_data。
    """
    try:
        api._complete_qr_login(login_data)
        return {"status": "success", "available": api.available}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/homes", summary="获取家庭列表")
def get_homes(api: mijiaAPI = Depends(get_api)):
    return api.get_homes_list()

@app.get("/devices", summary="获取设备列表")
def get_devices(home_id: Optional[str] = None, api: mijiaAPI = Depends(get_api)):
    return api.get_devices_list(home_id=home_id)

@app.get("/shared_devices", summary="获取共享设备列表")
def get_shared_devices(api: mijiaAPI = Depends(get_api)):
    return api.get_shared_devices_list()

@app.get("/scenes", summary="获取场景列表")
def get_scenes(home_id: Optional[str] = None, api: mijiaAPI = Depends(get_api)):
    return api.get_scenes_list(home_id=home_id)

@app.post("/scenes/{scene_id}/run", summary="执行场景")
def run_scene(scene_id: str, home_id: Optional[str] = None, api: mijiaAPI = Depends(get_api)):
    try:
        ret = api.run_scene(scene_id, home_id)
        return {"status": "success", "data": ret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/devices/prop/get", summary="获取设备属性")
def get_props(props: List[Prop], api: mijiaAPI = Depends(get_api)):
    try:
        req_data = [p.model_dump(exclude_none=True) for p in props]
        ret = api.get_devices_prop(req_data)
        return {"status": "success", "data": ret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/devices/prop/set", summary="设置设备属性")
def set_props(props: List[Prop], api: mijiaAPI = Depends(get_api)):
    try:
        req_data = [p.model_dump() for p in props]
        ret = api.set_devices_prop(req_data)
        return {"status": "success", "data": ret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/devices/action/run", summary="执行设备动作")
def run_action(action: Action, api: mijiaAPI = Depends(get_api)):
    try:
        req_data = action.model_dump(exclude_none=True, by_alias=True)
        ret = api.run_action(req_data)
        return {"status": "success", "data": ret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consumable_items", summary="获取耗材列表")
def get_consumables(home_id: Optional[str] = None, api: mijiaAPI = Depends(get_api)):
    return api.get_consumable_items(home_id=home_id)

@app.post("/statistics", summary="获取统计数据")
def get_statistics(query: StatQuery, api: mijiaAPI = Depends(get_api)):
    try:
        ret = api.get_statistics(query.model_dump())
        return {"status": "success", "data": ret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
