# recommender/justifier.py
from models.task_model import Task

def generate_task_reason(task: Task) -> str:
    """
    根据任务标签与用户兴趣生成解释文本 / Generate task explanation from task tags and interests
    """
    return f"任务 {task.name} 是基于你的兴趣标签 {task.tags} 推荐的，旨在帮助你成长。"
