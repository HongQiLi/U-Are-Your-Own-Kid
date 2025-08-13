# test/test_prompt.py

from models.user_profile import UserProfile
from utils.prompt_builder import build_prompt

def test_prompt_generation():
    dummy_user = UserProfile(
        name="Alice",
        age=14,
        goals=["Improve creativity", "Build confidence"],
        survey={"interests": ["drawing", "storytelling"]},
        availability=["Monday afternoon", "Saturday morning"]
    )

    prompt = build_prompt(dummy_user)
    print("Generated prompt:\n")
    print(prompt)

# manually run
if __name__ == "__main__":
    test_prompt_generation()
