from faker import Faker
import random
from models.user_model import UserProfile
from recommender.core import recommend_tasks

fake = Faker("zh_CN")

def test_fake_users():
    for _ in range(5):
        profile = UserProfile(
            name=fake.name(),
            age=random.randint(10, 17),
            goals=[random.choice(["提升表达能力", "增强体能", "探索兴趣"])],
            survey={"interests": [random.choice(["写作", "篮球", "编程", "美术"])]},
            availability=["周一下午", "周三晚上"]
        )
        result = recommend_tasks(profile)
        assert result is not None
        print(profile.name, "推荐结果：", result)
