# utils/prompt_builder.py

def build_prompt(user_profile):
    """
    Construct a natural language prompt from the user profile
    to send to an LLM (OpenAI, Cohere, etc.) for recommendation explanation.
    """

    name = user_profile.name
    age = user_profile.age
    goals = ", ".join(user_profile.goals)
    interests = ", ".join(user_profile.survey.get("interests", []))
    availability = ", ".join(user_profile.availability)

    prompt = f"""
You are a personalized growth planner AI. Here is a user profile:

Name: {name}
Age: {age}
Goals: {goals}
Interests: {interests}
Available Time: {availability}

Please explain in natural English why the following task was recommended to this user based on their goals, interests, and available time.
    """.strip()

    return prompt
