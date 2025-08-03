# main.py
# 应用主入口 / Application Entry Point

from fastapi import FastAPI
from routers import user, schedule, recommender, feedback, parent, calendar_sync

# 创建 FastAPI 实例 / Create FastAPI app
app = FastAPI(
    title="AI Growth Planner",
    description="一个支持个性化成长路径规划的智能平台 / An intelligent platform for personalized growth planning",
    version="1.0.0"
)

# 注册各功能模块对应的路由 / Register routers for each module
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
app.include_router(recommender.router, prefix="/recommend", tags=["Recommender"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(parent.router, prefix="/parent", tags=["Parent"])
app.include_router(calendar_sync.router, prefix="/calendar", tags=["Calendar"])

# 运行方法（部署或本地运行）/ Run the app:
# uvicorn main:app --reload
