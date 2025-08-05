# routers/feedback.py
# User feedback collection API

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Feedback 数据结构定义 / Feedback Schema
class Feedback(BaseModel):
    user_id: str               # 用户唯一ID
    task_name: str             # 反馈对应的任务名
    rating: int                # 任务评分（例如1-5）
    comment: Optional[str] = None  # 可选文字评价

# 临时存储用户反馈（生产环境请改为数据库）/ In-memory feedback store
feedback_db = []

@router.post("/feedback/submit")
def submit_feedback(feedback: Feedback):
    """
    Submit user feedback for a specific task.

    Parameters:
    - user_id: unique identifier of the user
    - task_name: the task being reviewed
    - rating: numeric score (e.g. 1–5)
    - comment: optional additional comment

    Returns:
    - message: confirmation
    """
    feedback_db.append(feedback)
    return {"message": "Feedback submitted successfully."}

@router.get("/feedback/user/{user_id}")
def get_feedback_by_user(user_id: str):
    """
    Retrieve all feedback submitted by a specific user.
    """
    user_feedback = [f for f in feedback_db if f.user_id == user_id]
    if not user_feedback:
        raise HTTPException(status_code=404, detail="No feedback found for this user.")
    return user_feedback
