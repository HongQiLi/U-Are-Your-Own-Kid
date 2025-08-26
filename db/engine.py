# db/engine.py
# CN: 异步引擎 + 会话工厂 + 初始化建表
# EN: Async engine + session factory + init tables

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")

async_engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

async def init_db():
    # CN: 仅当你切到真实模式时，才导入真实用户表并创建；开发期不强制。
    # EN: Import real user tables and create only when in real mode; dev mode won't require them.
    from services.auth import USE_STUB
    if not USE_STUB:
        from models.auth_user_real import Base as AuthBase
        async with async_engine.begin() as conn:
            await conn.run_sync(AuthBase.metadata.create_all)
