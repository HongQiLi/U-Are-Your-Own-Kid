# utils/schedule_optimizer.py
# 任务安排优化器 / Task Scheduling Optimizer

from typing import List, Dict


def generate_schedule(task_list: List[Dict]) -> List[Dict]:
    """
    模拟任务时间安排生成器。
    Simulated scheduler that returns tasks with mock start/end times.

    参数 / Params:
        task_list (List[Dict]): 原始任务列表，如 [{'name': 'Read', 'duration': 30}]

    返回 / Returns:
        List[Dict]: 增加了开始和结束时间的任务列表
    """
    scheduled_tasks = []
    current_start = 9 * 60  # 从早上9:00开始，以分钟计 / Start at 9:00 AM

    for task in task_list:
        name = task.get("name", "Unnamed Task")
        duration = task.get("duration", 30)  # 默认为30分钟

        start_hour = current_start // 60
        start_min = current_start % 60
        end_time = current_start + duration
        end_hour = end_time // 60
        end_min = end_time % 60

        scheduled_tasks.append({
            "name": name,
            "duration": duration,
            "start_time": f"{start_hour:02d}:{start_min:02d}",
            "end_time": f"{end_hour:02d}:{end_min:02d}"
        })

        current_start = end_time  # 下一个任务的开始时间 / Update current_start

    return scheduled_tasks
