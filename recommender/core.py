# recommender/core.py
# 推荐引擎核心逻辑 / Task Recommender Core Logic

from utils.schedule_optimizer import generate_schedule
from utils.interest_extractor import extract_interest_from_survey
from models.user_model import UserProfile
from models.task_model import Task
from recommender.contextual_rules import get_optimal_task_type_by_time

# 推荐函数：提取兴趣并生成任务计划 / Recommend tasks based on interests and availability and human healthy grow
async def recommend_tasks(user_profile: UserProfile) -> list[Task]:
    """
    推荐任务：考虑兴趣、目标、作息、时间科学等 / Recommend tasks based on user context and health science
    """
    interests = extract_interest_from_survey(user_profile.survey)
    availability = user_profile.availability

    tasks = []

    for time_slot in availability:
        optimal_type = get_optimal_task_type_by_time(time_slot)
        for interest in interests:
            task_name = f"{interest} 训练 - {optimal_type}"
            task = Task(
                name=task_name,
                tags=[interest, optimal_type, "成长任务"],
                scheduled_time=time_slot
            )
            tasks.append(task)

    return tasks

