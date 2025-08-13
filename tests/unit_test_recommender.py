# tests/test_recommender.py
# 推荐系统单元测试 / Recommender logic unit test

from models.user_profile import UserProfile
from recommender.core import recommend_tasks

def test_recommend_tasks():
    dummy_user = UserProfile(
        name="Test",
        age=14,
        survey={"Q1": "science", "Q2": "robot"},
        availability={"Monday": ["16:00", "17:00"]}
    )
    result = recommend_tasks(dummy_user)
    assert result is not None
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
