# recommender/core.py
# Task Recommender Core Logic

from utils.schedule_optimizer import generate_schedule
from utils.interest_extractor import extract_interest_from_survey
from models.user_model import UserProfile
from models.task_model import Task
from recommender.contextual_rules import get_optimal_task_type_by_time

# Main recommendation function
async def recommend_tasks(user_profile: UserProfile) -> list[Task]:
    """
    Generate personalized growth tasks based on user's interests, goals,
    availability, and scientifically optimized time-use patterns.

    Steps:
    1. Extract key interests from the user's survey.
    2. Loop through each available time slot.
    3. Determine the optimal task type for that time (e.g., physical, creative, cognitive).
    4. Combine interest and task type to generate a contextual task suggestion.
    5. Return a list of Task objects with schedule and tags.

    This method is designed to ensure that tasks:
    - Align with user's personal interests and goals,
    - Fit into their realistic weekly availability,
    - Follow healthy human productivity rhythms (e.g., avoid intense tasks late at night),
    - Provide semantic tags for downstream explanation or feedback modules.

    Args:
        user_profile (UserProfile): The input profile including interests, goals, availability.

    Returns:
        list[Task]: A list of personalized, time-aware tasks.
    """
    interests = extract_interest_from_survey(user_profile.survey)
    availability = user_profile.availability

    tasks = []

    for time_slot in availability:
        optimal_type = get_optimal_task_type_by_time(time_slot)  # e.g., "creative work", "light reading"
        for interest in interests:
            task_name = f"{interest} Training - {optimal_type}"
            task = Task(
                name=task_name,
                tags=[interest, optimal_type, "growth_task"],
                scheduled_time=time_slot
            )
            tasks.append(task)

    return tasks
