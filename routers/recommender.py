# routers/recommender.py
# 推荐系统路由 / Recommender API Router

from fastapi import APIRouter, HTTPException
from models.user_model import UserProfile
from recommender.core import recommend_tasks
from typing import List
from models.task_model import Task

router = APIRouter()

# =========================
# POST /recommend/tasks
# 生成推荐任务列表
# =========================
@router.post("/recommend/tasks", response_model=List[Task])
async def get_recommended_tasks(user_profile: UserProfile):
    """
    Generate a list of recommended tasks based on user's profile:
    - Interests extracted from the survey
    - Daily availability
    - Scientific patterns for optimal timing (e.g., morning learning, evening reflection)
    """
    try:
        tasks = await recommend_tasks(user_profile)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

