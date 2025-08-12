# main.py - 精简版，只保留 OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 路由模块（根据你的项目需要保留）
from routers import user, schedule, recommender, feedback, parent, calendar_sync

# 数据库初始化
from db.engine import init_db

# 只保留 OpenAI 客户端
from utils.openai_client import generate_openai_reply as openai_reply


app = FastAPI(
    title="U-Are-Your-Own-Kid",
    description="An intelligent platform for personalized growth planning",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发期全开放
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时初始化数据库
@app.on_event("startup")
async def on_startup():
    await init_db()


# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/front", StaticFiles(directory="front"), name="front")


# 首页
@app.get("/", include_in_schema=False)
def serve_home():
    return FileResponse("front/app.html")


# 健康检查
@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}


# OpenAI 测试接口
@app.get("/test-llm")
async def test_llm(prompt: str = Query("Give me 3 creative ways to help kids build self-discipline.")):
    try:
        openai_output = openai_reply(prompt)
    except Exception as e:
        openai_output = f"OpenAI error: {str(e)}"

    return {"openai": openai_output}


# 注册业务路由
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
app.include_router(recommender.router, prefix="/recommend", tags=["Recommender"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(parent.router, prefix="/parent", tags=["Parent"])
app.include_router(calendar_sync.router, prefix="/calendar", tags=["Calendar"])
