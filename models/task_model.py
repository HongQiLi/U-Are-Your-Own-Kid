# models/task_model.py
# 任务与反馈结构定义 / Task and Feedback Schemas

from pydantic import BaseModel
from typing import Optional

class Task(BaseModel):
    task_id: str       # 任务编号 / Task ID
    title: str         # 任务标题 / Title of task
    description: str   # 任务描述 / Detailed instruction
    duration: int      # 持续时长（分钟） / Duration in minutes

class TaskFeedback(BaseModel):
    task_id: str           # 任务 ID / Task being evaluated
    rating: float          # 用户打分（0-1）/ Rating score (0.0 - 1.0)
    difficulty: float      # 用户感知难度（0-1）/ Perceived difficulty (0.0 - 1.0)
    time_efficiency: float # 时间效率（0-1）/ Time efficiency (0.0 - 1.0)
