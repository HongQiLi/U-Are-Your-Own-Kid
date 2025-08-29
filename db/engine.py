# db/engine.py
# CN: 异步引擎 + 会话工厂 + 初始化建表 + 数据库自检
# EN: Async engine + session factory + init tables + DB introspection

import os
from typing import Dict, List

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")

# 若使用 sqlite 文件，确保目录存在 / Ensure sqlite dir exists
if DATABASE_URL.startswith("sqlite+aiosqlite:///"):
    db_path = DATABASE_URL.replace("sqlite+aiosqlite:///", "", 1)
    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

async_engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
# ✅ 修复：只赋值一次；并明确 class_=AsyncSession
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

async def init_db() -> None:
    """
    CN:
      - 非 Stub 模式：创建 fastapi-users 真实用户表（SQLAlchemy Declarative Base）
      - 所有模式：创建 SQLModel 业务表（Event 等）
    EN:
      - Non-stub: create real auth tables (SQLAlchemy Declarative Base)
      - All modes: create SQLModel business tables (Event, etc.)
    """
    from services.auth import USE_STUB

    async with async_engine.begin() as conn:
        if not USE_STUB:
            # 真实用户表（如果你在生产启用 fastapi-users）
            from models.auth_user_real import Base as AuthBase
            await conn.run_sync(AuthBase.metadata.create_all)

        # 关键：导入 SQLModel 模型，让 metadata 收集到表
        import models.event_model  # noqa: F401
        # 若还有其他 SQLModel 表，在此一起导入
        # import models.schedule_model  # noqa: F401
        # import models.user_profile   # noqa: F401

        await conn.run_sync(SQLModel.metadata.create_all)

async def inspect_db() -> Dict[str, List[str]]:
    """CN: 返回 {表名: [列,...]}；EN: Return {table: [cols,...]}"""
    def _sync(conn):
        ins = inspect(conn)
        tables = {}
        for t in ins.get_table_names():
            cols = [c["name"] for c in ins.get_columns(t)]
            tables[t] = cols
        return tables

    async with async_engine.connect() as conn:
        return await conn.run_sync(_sync)

async def log_db_overview(prefix: str = "[DB]") -> None:
    """CN: 打印 URL/表/列；EN: Print URL/tables/columns"""
    info = await inspect_db()
    print(f"{prefix} URL = {DATABASE_URL}")
    for t, cols in info.items():
        print(f"{prefix} {t}: {cols}")
