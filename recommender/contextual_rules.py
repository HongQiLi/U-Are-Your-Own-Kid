#recommender/contextual_rules

def get_optimal_task_type_by_time(time_slot: str) -> str:
    """
    根据时间返回推荐任务类型 / Recommend task type based on circadian rhythm
    """
    if "07" <= time_slot[:2] <= "10":
        return "学习"
    elif "12" <= time_slot[:2] <= "14":
        return "午休或轻松阅读"
    elif "16" <= time_slot[:2] <= "18":
        return "运动"
    else:
        return "灵活任务"
