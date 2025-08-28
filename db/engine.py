# db/engine.py
# CN: 异步引擎 + 会话工厂 + 初始化建表 + 数据库自检
# EN: Async engine + session factory + init tables + DB introspection

import os
from typing import Dict, List
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy import inspect
from sqlmodel import SQLModel

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")

async_engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session_maker = async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

async def init_db() -> None:
    """
    CN: 初始化数据库：创建 fastapi-users 的真实用户表（若启用），并创建所有 SQLModel 表（Event 等）。
    EN: Initialize DB: create real auth tables (if enabled) and all SQLModel tables (Event, etc.).
    """
    # 1) 可选：创建“真实用户表”
    from services.auth import USE_STUB
    async with async_engine.begin() as conn:
        if not USE_STUB:
            # 注意：这套 Base 是 SQLAlchemy Declarative Base（非 SQLModel）
            # Note: This Base is SQLAlchemy Declarative Base (not SQLModel)
            from models.auth_user_real import Base as AuthBase
            await conn.run_sync(AuthBase.metadata.create_all)

        # 2) 创建所有 SQLModel 表（关键：先导入模型，才能写入 metadata）
        #    Import your SQLModel models BEFORE create_all, so they are registered.
        from models import event_model  # 例如：Event 表
        # 如有其他 SQLModel 表，也在这里 import：schedule_model, user_profile 等

        await conn.run_sync(SQLModel.metadata.create_all)

async def inspect_db() -> Dict[str, List[str]]:
    """
    CN: 返回 {表名: [列,...]} 的结构，用于在代码里检查“哪些表被建了、有哪些列”。
    EN: Return {table_name: [columns,...]} to verify what tables/columns exist at runtime.
    """
    def _sync_inspect(sync_conn):
        ins = inspect(sync_conn)
        tables = {}
        for t in ins.get_table_names():
            cols = [col["name"] for col in ins.get_columns(t)]
            tables[t] = cols
        return tables

    async with async_engine.connect() as conn:
        tables = await conn.run_sync(_sync_inspect)
        return tables

async def log_db_overview(prefix: str = "[DB]") -> None:
    """
    CN: 启动时打印数据库总览（URL + 表 + 列）。
    EN: Print DB overview (URL + tables + columns) at startup.
    """
    info = await inspect_db()
    print(f"{prefix} URL = {DATABASE_URL}")
    for t, cols in info.items():
        print(f"{prefix} {t}: {cols}")
