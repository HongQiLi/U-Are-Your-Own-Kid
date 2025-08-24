# routers/schedule.py
# ===========================================================
# 用户日程管理路由（快速安全版：用内存 + 登录鉴权）
# English: User schedule management router (quick safe version: in-memory + auth)
# ===========================================================

# -------- 导入依赖 / Import dependencies --------
from fastapi import APIRouter, HTTPException, Depends
# APIRouter: 用于创建路由分组 / For grouping endpoints
# HTTPException: 用于抛出 HTTP 错误响应 / For returning HTTP errors
# Depends: 用于依赖注入（这里用来获取当前登录用户）/ For dependency injection (get current user)

from pydantic import BaseModel
# BaseModel: 用于定义请求体数据结构 / For request body schema definition

from typing import Dict
# Dict: 用于类型注解，表示字典类型 / Type hint for dictionary

from services.auth import current_active_user
# current_active_user: 登录鉴权依赖函数，会根据用户 token 返回用户信息 / Auth dependency to get user from token

from models.auth_user import User
# User: 用户数据模型（auth_user.py 中定义）/ User model defined in auth_user.py

# -------- 创建路由器 / Create APIRouter instance --------
router = APIRouter()

# -------- 内存数据库（临时存储） / In-memory fake DB --------
# key: 用户ID（字符串），value: 可用时间表（字典）
# key: user ID (string), value: availability schedule (dict)
fake_schedule_db: dict[str, Dict[str, int]] = {}


# -------- 请求体数据结构 / Request body schema --------
class UserSchedule(BaseModel):
    # availability: 字典类型，key 是星期缩写，value 是分钟数
    # availability: Dict where key = weekday abbreviation, value = minutes available
    availability: Dict[str, int]  # e.g. {"Mon": 60, "Tue": 45, "Wed": 0}


# -------- 上传或更新日程安排 / Upload or update schedule --------
@router.post("/schedule")
def upload_schedule(
    schedule: UserSchedule,
    user: User = Depends(current_active_user)  
    # 从登录状态获取当前用户对象
    # Get current logged-in user from token
):
    """
    上传或更新当前用户的日程安排
    Upload or update the schedule for the current user
    """
    # 使用用户 ID 作为 key 保存日程数据
    # Use user ID as the key to store schedule
    fake_schedule_db[str(user.id)] = schedule.availability

    # 返回确认信息 / Return confirmation
    return {
        "message": "Schedule uploaded successfully",  # 上传成功 / Upload success
        "user_id": str(user.id),                      # 用户 ID / User ID
        "availability": schedule.availability         # 当前保存的日程 / Current saved schedule
    }


# -------- 获取当前用户的日程安排 / Get current user's schedule --------
@router.get("/schedule")
def get_schedule(
    user: User = Depends(current_active_user)  
    # 同样从 token 获取用户身份
    # Get user identity from token
):
    """
    获取当前登录用户的日程安排
    Retrieve the schedule of the current logged-in user
    """
    # 根据用户 ID 从内存数据库中查找 / Get schedule from in-memory DB
    data = fake_schedule_db.get(str(user.id))

    # 如果找不到，返回 404 错误 / If not found, return 404
    if not data:
        raise HTTPException(404, "Schedule not found.")

    # 返回结果 / Return result
    return {
        "user_id": str(user.id),   # 用户 ID / User ID
        "availability": data       # 日程安排 / Schedule data
    }
