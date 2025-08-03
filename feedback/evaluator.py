# feedback/evaluator.py
# 任务反馈评估模块 / Feedback Evaluator

from models.task_model import TaskFeedback

# 输入任务反馈，计算任务完成度得分 / Evaluate completion quality based on feedback
def evaluate_feedback(feedback: TaskFeedback) -> float:
    score = (feedback.rating + (1 - feedback.difficulty) + feedback.time_efficiency) / 3
    return round(score, 2)
