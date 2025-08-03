# models/schedule_model.py
# 日程结构 / User Schedule Schema

from pydantic import BaseModel
from typing import List
from models.task_model import Task

class UserSchedule(BaseModel):
    user_id: str         # 用户 ID / User ID
    date: str            # 日期（YYYY-MM-DD）/ Date
    tasks: List[Task]    # 当日任务列表 / Task list for the day
