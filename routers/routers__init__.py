# routers/routers__init__.py
# 初始化 routers 包 / Initialize routers package

from .user import router as user_router
from .schedule import router as schedule_router
from .recommender import router as recommender_router
from .feedback import router as feedback_router
from .parent import router as parent_router
from .calendar_sync import router as calendar_sync_router

# 把所有路由放在一个列表里，方便 main.py 引用
all_routers = [
    user_router,
    schedule_router,
    recommender_router,
    feedback_router,
    parent_router,
    calendar_sync_router,
]

