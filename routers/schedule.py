# routers/schedule.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

# =========================
# Temporary in-memory DB to store user schedules
# （在生产中应替换为数据库）
# =========================
fake_schedule_db = {}

# =========================
# Request Model: UserSchedule
# =========================
class UserSchedule(BaseModel):
    user_id: str
    availability: Dict[str, int]  # e.g., {"Mon": 60, "Tue": 45, "Wed": 0, ...}

# =========================
# POST /schedule/upload
# 用户上传日程安排
# =========================
@router.post("/schedule/upload")
def upload_schedule(schedule: UserSchedule):
    """
    Upload or update a user's daily availability schedule.
    The schedule will be stored in memory and used by the recommendation engine.
    """
    fake_schedule_db[schedule.user_id] = schedule.availability
    return {
        "message": "Schedule uploaded successfully.",
        "user_id": schedule.user_id,
        "availability": schedule.availability
    }

# =========================
# GET /schedule/{user_id}
# 获取用户的日程安排
# =========================
@router.get("/schedule/{user_id}")
def get_schedule(user_id: str):
    """
    Retrieve a user's daily availability schedule.
    """
    schedule = fake_schedule_db.get(user_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found.")
    return {
        "user_id": user_id,
        "availability": schedule
    }
