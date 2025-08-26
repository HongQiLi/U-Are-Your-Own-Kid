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

# 鉴权模式开关：开发用 Stub，生产切换 fastapi-users
# Auth mode switch: stub in dev, fastapi-users in prod
from services.auth import USE_STUB

# 路由集中注册（避免在这里逐个导入）
# Centralized router registry (avoid per-file imports here)
from routers import all_routers

# 数据库初始化（在真实模式时建表；Stub 模式会被内部跳过）
# DB init (creates tables in real mode; skipped internally in stub mode)
from db.engine import init_db

# OpenAI 客户端（保留测试接口）
# OpenAI client (keep the test endpoint)
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
# CORS 中间件配置 / CORS middleware
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 开发期全开放；生产请改为白名单 / Allow all in dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# 启动事件：初始化数据库 / Startup: init DB
# ========================================
@app.on_event("startup")
async def on_startup():
    """
    在应用启动时初始化数据库：
    - 真实模式（USE_STUB=False）会创建用户表等
    - 开发 Stub 模式下，init_db 内部会跳过建表
    Initialize the database on startup:
    - Real mode (USE_STUB=False): create auth tables
    - Stub mode: init_db will no-op internally
    """
    try:
        await init_db()
    except Exception as e:
        # 防御性处理，避免启动失败；错误会打印出来便于排查
        # Defensive: don't crash on init; print error for diagnosing
        print("DB init skipped or failed:", e)


# ========================================
# 静态文件挂载 / Static file mounts
# ========================================
app.mount("/static", StaticFiles(directory="static"), name="static")  # 静态资源 / Static assets
app.mount("/front", StaticFiles(directory="front"), name="front")    # 前端页面 / Frontend pages


# ========================================
# 首页路由 / Homepage
# ========================================
@app.get("/", include_in_schema=False)
def serve_home():
    """
    返回首页 HTML 页面
    Return the homepage HTML file
    """
    return FileResponse("front/app.html")


# ========================================
# 健康检查 / Health check
# ========================================
@app.get("/health", include_in_schema=False)
def health():
    """
    检查 API 是否正常运行
    Check if the API is running normally
    """
    return {"ok": True}


# ========================================
# OpenAI 测试接口 / OpenAI test endpoint
# ========================================
@app.get("/test-llm")
async def test_llm(
    prompt: str = Query("Give me 3 creative ways to help kids build self-discipline.")
):
    """
    使用 OpenAI 生成回答
    Generate a response using the OpenAI client
    """
    try:
        openai_output = openai_reply(prompt)
    except Exception as e:
        openai_output = f"OpenAI error: {str(e)}"
    return {"openai": openai_output}


# ========================================
# 注册业务功能路由（集中注册）
# Register business feature routers (centralized)
# ========================================
for r, prefix, tags in all_routers:
    # 注意：各子路由文件内请使用“相对路径”装饰器（@router.get("")），避免双前缀
    # Note: use relative decorators inside sub-routers to avoid double prefix
    app.include_router(r, prefix=prefix, tags=tags)


# ========================================
# 仅在真实模式下，注册登录/注册/用户管理路由（fastapi-users）
# Register auth/register/users routes ONLY in real mode (fastapi-users)
# ========================================
if not USE_STUB:
    # 延迟导入以避免 Stub 模式下加载 fastapi-users
    # Lazy-import to avoid loading fastapi-users in stub mode
    from services.auth import fastapi_users, auth_backend
    from models.auth_schemas import UserRead, UserCreate, UserUpdate

    # JWT 登录 / JWT login
    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/auth/jwt",
        tags=["auth"],
    )
    # 用户注册 / Registration
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    # 用户管理（选用）/ Users management (optional)
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )
