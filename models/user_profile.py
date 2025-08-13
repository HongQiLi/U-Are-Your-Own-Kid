# models/user_profile.py
# 用户画像结构定义 / User Profile Schema

from pydantic import BaseModel
from typing import Dict

class UserProfile(BaseModel):
    user_id: str  # 用户唯一标识 / Unique user ID
    name: str     # 用户姓名 / Name
    survey: str   # 兴趣调查问卷原文 / Raw survey input
    availability: Dict[str, int]  # 每天可用时长（如 {"Mon": 60, "Tue": 45}）/ Daily available time in minutes
