# recommender/core.py
# 推荐引擎核心逻辑 / Task Recommender Core Logic

from utils.interest_extractor import extract_interest_from_survey
from utils.schedule_optimizer import generate_schedule
from models.user_model import UserProfile
from models.task_model import Task

# 推荐函数：提取兴趣并生成任务计划 / Recommend tasks based on interests and availability
async def recommend_tasks(user_profile: UserProfile) -> list[Task]:
    interests = extract_interest_from_survey(user_profile.survey)
    plan = generate_schedule(interests, user_profile.availability)
    return plan
