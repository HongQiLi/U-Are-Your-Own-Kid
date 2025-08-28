# ===============================
# main.py
# 应用主入口 / Application Entry Point
# ===============================

import os
from dotenv import load_dotenv  # 用于加载 .env 文件中的环境变量 / Load env vars from .env
load_dotenv()

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 鉴权模式开关：开发用 Stub，生产切换 fastapi-users
# Auth mode switch: stub in dev, fastapi-users in prod
from services.auth import USE_STUB

# 路由集中注册（避免在这里逐个导入）
# Centralized router registry
from routers import all_routers

# 数据库初始化 + 概览输出（见 db/engine.py）
# DB init + overview (see db/engine.py)
from db.engine import init_db, log_db_overview

# OpenAI 客户端（保留测试接口）
# OpenAI client (keep the test endpoint)
from utils.openai_client import generate_openai_reply as openai_reply


# ========================================
# 创建 FastAPI 应用实例 / Create FastAPI app instance
# ========================================
app = FastAPI(
    title="U-Are-Your-Own-Kid",
    description="An intelligent platform for personalized growth planning",
    version="1.0.0",
)


# ========================================
# CORS 中间件配置 / CORS middleware
# 开发期全放开；生产记得换成前端/Widget 域名白名单
# Allow all in dev; restrict to your frontend/widget domains in prod
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO(prod): replace with whitelist
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# 启动事件：初始化数据库 + 打印数据库概览
# Startup: init DB + print DB overview
# ========================================
@app.on_event("startup")
async def on_startup():
    """
    启动阶段执行：
    1) 初始化数据库（创建 fastapi-users 的真实用户表 + 所有 SQLModel 表，如 Event）
    2) 打印数据库概览（URL、表名、列名），便于确认 schema 是否正确

    On startup:
    1) Initialize DB (auth tables + all SQLModel tables like Event)
    2) Print DB overview (URL, tables, columns) to verify schema
    """
    # 1) 初始化失败则终止启动（fail-fast），更容易定位问题
    #    Fail fast on init errors for easier diagnostics
    try:
        await init_db()
    except Exception as e:
        raise RuntimeError(f"DB init failed: {e}") from e

    # 2) 打印数据库概览（可选；失败不阻断启动）
    #    Print DB overview (optional; non-fatal)
    try:
        await log_db_overview(prefix="[DB]")
    except Exception as e:
        print("DB overview skipped:", e)


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
    """返回首页 HTML 页面 / Return the homepage HTML file"""
    return FileResponse("front/app.html")


# ========================================
# 健康检查 / Health checks
# ========================================
@app.get("/health", include_in_schema=False)
def health():
    """检查 API 是否正常运行 / Liveness check"""
    return {"ok": True}

@app.get("/healthz", include_in_schema=False)
def healthz():
    """K8s 风格健康检查 / K8s-style health check"""
    return {"status": "ok"}


# ========================================
# OpenAI 测试接口 / OpenAI test endpoint
# ========================================
@app.get("/test-llm")
async def test_llm(
    prompt: str = Query("Give me 3 creative ways to help kids build self-discipline.")
):
    """使用 OpenAI 生成回答 / Generate a response using the OpenAI client"""
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
    # 子路由文件应使用相对路径装饰器（@router.get("")），避免双前缀
    # Sub-routers should use relative decorators to avoid double prefix
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
    # 用户管理（按需开放）/ Users management (optional)
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )
