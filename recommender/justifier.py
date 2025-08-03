# recommender/justifier.py
def generate_task_reason(task: Task) -> str:
    """
    更自然的推荐理由 / Natural task reasoning
    """
    base = f"任务「{task.name}」结合你的兴趣和成长目标，"
    if "运动" in task.tags:
        reason = base + "并安排在你专注力较低的时段，帮助你调节状态，提升整体效率。"
    elif "学习" in task.tags:
        reason = base + "并安排在你认知活跃的时间，有利于深入思考与知识内化。"
    else:
        reason = base + "是整体成长路径中的关键组成部分，建议你按时完成。"
    return reason
