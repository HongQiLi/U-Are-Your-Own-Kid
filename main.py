# ===============================
# main.py
# 应用主入口 / Application Entry Point
# ===============================

import os
from dotenv import load_dotenv  # 用于加载 .env 文件中的环境变量 / Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 导入路由模块（保留已有功能模块）
# Import routers (keep your existing functional modules)
from routers import user, schedule, recommender, feedback, parent, calendar_sync

# 数据库初始化方法
# Database initialization function
from db.engine import init_db

# 只保留 OpenAI 客户端方法 / Keep only the OpenAI client method
from utils.openai_client import generate_openai_reply as openai_reply


# ========================================
# 创建 FastAPI 应用实例 / Create FastAPI app instance
# ========================================
app = FastAPI(
    title="U-Are-Your-Own-Kid",  # API 文档标题 / API documentation title
    description="An intelligent platform for personalized growth planning",  # 描述 / Description
    version="1.0.0",  # 版本号 / Version
)


# ========================================
# CORS 中间件配置
# CORS middleware settings (allow cross-origin requests)
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名访问（开发环境建议全开放）/ Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法 / Allow all HTTP methods
    allow_headers=["*"],  # 允许所有请求头 / Allow all headers
)


# ========================================
# 启动事件：初始化数据库
# Startup event: initialize database
# ========================================
@app.on_event("startup")
async def on_startup():
    await init_db()  # 创建表结构或连接数据库 / Create tables or connect to DB


# ========================================
# 静态文件挂载
# Mount static file directories
# ========================================
app.mount("/static", StaticFiles(directory="static"), name="static")  # 静态资源 / Static resources
app.mount("/front", StaticFiles(directory="front"), name="front")    # 前端页面 / Frontend pages


# ========================================
# 首页路由
# Homepage route
# ========================================
@app.get("/", include_in_schema=False)
def serve_home():
    """
    返回首页 HTML 页面
    Return the homepage HTML file
    """
    return FileResponse("front/app.html")


# ========================================
# 健康检查路由
# Health check route
# ========================================
@app.get("/health", include_in_schema=False)
def health():
    """
    用于检查 API 是否正常运行
    Check if the API is running normally
    """
    return {"ok": True}


# ========================================
# OpenAI 测试接口
# OpenAI test API
# ========================================
@app.get("/test-llm")
async def test_llm(
    prompt: str = Query("Give me 3 creative ways to help kids build self-discipline.")
):
    """
    使用 OpenAI 生成回答
    Generate a response using OpenAI model
    """
    try:
        openai_output = openai_reply(prompt)  # 调用 OpenAI 客户端生成结果 / Call OpenAI client
    except Exception as e:
        openai_output = f"OpenAI error: {str(e)}"

    return {"openai": openai_output}


# ========================================
# 注册业务功能路由
# Register business feature routers
# ========================================
app.include_router(user.router, prefix="/user", tags=["User"])               # 用户管理 / User management
app.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])   # 日程管理 / Schedule management
app.include_router(recommender.router, prefix="/recommend", tags=["Recommender"])  # 推荐系统 / Recommender
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])   # 用户反馈 / Feedback
app.include_router(parent.router, prefix="/parent", tags=["Parent"])         # 家长模块 / Parent module
app.include_router(calendar_sync.router, prefix="/calendar", tags=["Calendar"])  # 日历同步 / Calendar sync
