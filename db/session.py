# db/session.py
# CN: 统一异步会话依赖（保持 import 兼容）
# EN: Unified async session dependency (keeps import compatibility)

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .engine import async_session_maker  # 复用同一个异步引擎 / reuse the same async engine

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    CN: FastAPI 依赖项：获取一个异步数据库会话。
    EN: FastAPI dependency that yields an AsyncSession.
    """
    async with async_session_maker() as session:
        yield session
