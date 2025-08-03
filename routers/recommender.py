# routers/recommender.py
# 推荐系统路由 / Recommender API Router

from fastapi import APIRouter
from models.user_model import UserProfile  # 导入用户画像模型 / Import user profile model
from models.task_model import Task         # 导入任务模型 / Import task schema
from recommender.core import recommend_tasks  # 导入推荐逻辑核心函数 / Import core recommendation function

router = APIRouter()  # 创建路由实例 / Create router instance

@router.post("/tasks", response_model=list[Task])
async def get_recommended_tasks(user_profile: UserProfile):
    """
    根据用户画像推荐任务 / Recommend tasks based on user profile
    """
    return await recommend_tasks(user_profile)
