# main.py
# 应用主入口 / Application Entry Point

import os
from dotenv import load_dotenv
load_dotenv()  # 读取 .env 环境变量 / load env vars

# ---- FastAPI 基础 ----
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# CORS：允许前端跨域访问（Codespaces 前端用 5500 端口时必须）/ CORS for frontend
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

# ---- 业务路由（你现有的模块）/ your existing routers ----
from routers import user, schedule, recommender, feedback, parent, calendar_sync

# ---- 工具类接口（你已有）/ util endpoints you already had ----
from utils.interest_extractor import extract_interest_from_survey
from utils.hf_client import generate_reply as hf_reply
from utils.cohere_client import generate_cohere_reply as cohere_reply
from utils.openai_client import generate_openai_reply as openai_reply

# ---- 认证与数据库（新增关键）/ auth & DB (important) ----
# services/auth.py 里装配了 fastapi-users；models/auth_user.py 定义了 User 模型
from services.auth import fastapi_users, auth_backend
from models.auth_user import UserRead, UserCreate, UserUpdate
from db.engine import init_db  # 数据库建表 / create tables on startup


# ============ 应用与配置 / App & Settings ============
class Settings(BaseSettings):
    # 允许的前端来源，开发期可以是 "*"；上线后请收紧
    # Allowed origins; use "*" for dev, restrict in prod
    ALLOWED_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI(
    title="U-Are-Your-Own-Kid",
    description="An intelligent platform for personalized growth planning",
    version="1.0.0",
)

# CORS 中间件：让浏览器前端能访问本后端 / CORS so frontend can call backend
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时自动建表（SQLite / Postgres 由 DATABASE_URL 决定）
# Auto-create tables on startup
@app.on_event("startup")
async def on_startup():
    await init_db()


# ============ 静态资源与首页 / Static and Home ============
# 不要把静态目录 mount 到 "/"，否则会覆盖自定义的首页路由
# Do NOT mount static at "/", otherwise it overrides the home route
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/front",  StaticFiles(directory="front"),  name="front")

# 健康检查 / Health check
@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}

# 网站首页：指向你要的前端页面 / Home -> your desired page
@app.get("/", include_in_schema=False)
def serve_home():
    # 想默认打开 calendar.html 就改成 "front/calendar.html"
    return FileResponse("front/app.html")

# （保留你原本的日历页面直达路由）
@app.get("/calendar-page", include_in_schema=False)
def serve_calendar():
    return FileResponse("front/calendar.html")


# ============ 实用测试接口 / Utility test endpoints ============
# 兴趣提取接口
@app.post("/test-interest")
async def test_interest_extraction(data: dict):
    return {"interests": extract_interest_from_survey(data)}

# LLM 三家对比（有 Key 才会返回真实，否则返回报错字符串）
@app.get("/test-llm")
async def test_llm(prompt: str = Query("Give me 3 creative ways to help kids build self-discipline.")):
    try:
        hf_output = hf_reply(prompt)
    except Exception as e:
        hf_output = f"HuggingFace error: {str(e)}"
    try:
        cohere_output = cohere_reply(prompt)
    except Exception as e:
        cohere_output = f"Cohere error: {str(e)}"
    try:
        openai_output = openai_reply(prompt)
    except Exception as e:
        openai_output = f"OpenAI error: {str(e)}"
    return {"huggingface": hf_output, "cohere": cohere_output, "openai": openai_output}


# ============ 认证路由（fastapi-users 自动生成）/ Auth routes ============
# /auth/register  注册；/auth/jwt/login 登录；/users 用户管理
# Register & login endpoints powered by fastapi-users
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"]
)


# ============ 业务路由注册 / Business routers ============
# 这些是你现有的业务模块；注意 schedule 路由内部要用 Depends(current_active_user)
# These are your existing routers; ensure schedule uses Depends(current_active_user) internally
app.include_router(user.router,         prefix="/user",     tags=["User"])
app.include_router(schedule.router,     prefix="/schedule", tags=["Schedule"])
app.include_router(recommender.router,  prefix="/recommend",tags=["Recommender"])
app.include_router(feedback.router,     prefix="/feedback", tags=["Feedback"])
app.include_router(parent.router,       prefix="/parent",   tags=["Parent"])
app.include_router(calendar_sync.router,prefix="/calendar", tags=["Calendar"])

# 运行示例 / How to run (Codespaces):
# python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
