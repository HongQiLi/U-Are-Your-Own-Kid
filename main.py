# main.py
# 应用主入口 / Application Entry Point

from fastapi import FastAPI
from routers import user, schedule, recommender, feedback, parent, calendar_sync
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from utils.interest_extractor import extract_interest_from_survey


# 首页路由
@app.get("/")
def serve_home():
    return FileResponse("front/index.html")

# 日历页面路由
@app.get("/calendar-page")
def serve_calendar():
    return FileResponse("front/calendar.html")

# 兴趣提取
@app.post("/test-interest")
async def test_interest_extraction(data: dict):
    return {
        "interests": extract_interest_from_survey(data)
    }

# 创建 FastAPI 实例 / Create FastAPI app
app = FastAPI(
    title="U-Are-Your-Own-Kid",
    description="An intelligent platform for personalized growth planning",
    version="1.0.0"
)


# 注册各功能模块对应的路由 / Register routers for each module
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
app.include_router(recommender.router, prefix="/recommend", tags=["Recommender"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(parent.router, prefix="/parent", tags=["Parent"])
app.include_router(calendar_sync.router, prefix="/calendar", tags=["Calendar"])
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 运行方法/ Run the app:
# uvicorn main:app --reload
