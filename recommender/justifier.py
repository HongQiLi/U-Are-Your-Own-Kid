# recommender/justifier.py
# 推荐理由解释模块 / Task Explanation Module

from models.task_model import Task
from models.user_model import UserProfile

def generate_task_reason(task: Task, user_profile: UserProfile) -> str:
    """
    根据兴趣、目标、时间、人体节律生成推荐理由
    Generate reason based on interests, goals, schedule and human efficiency rhythms
    """

    interest_match = ", ".join(tag for tag in task.tags if tag in user_profile.survey.get("interests", []))
    available_times = user_profile.availability
    time_mention = available_times[0] if available_times else "你空闲的时间段"

    return (
        f"基于你对「{interest_match}」的兴趣，我们建议你安排任务「{task.name}」。"
        f"该任务能帮助你提升相关技能，并匹配你在「{time_mention}」的可用时间。"
        f"同时我们结合青少年最佳专注时段与任务类型，设计了最优执行计划，帮助你高效达成目标。"
    )
