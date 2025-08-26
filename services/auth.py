# services/auth.py
# CN: 双模鉴权。开发(AUTH_STUB=1)返回 demo 用户；生产(AUTH_STUB=0)走 fastapi-users。
# EN: Dual-mode auth. Dev (AUTH_STUB=1) returns a demo user; Prod (AUTH_STUB=0) uses fastapi-users.

import os
from typing import Optional
from fastapi import Depends

USE_STUB = os.getenv("AUTH_STUB", "1") == "1"  # CN: 环境开关；EN: env switch

if USE_STUB:
    # ---------- 开发模式：桩用户 ----------
    # ---------- Dev mode: stub user ----------
    from pydantic import BaseModel

    class User(BaseModel):
        id: str = "demo"
        email: Optional[str] = "demo@example.com"
        is_active: bool = True

    async def current_active_user() -> User:
        # CN: 直接返回固定用户；EN: always return a fixed user
        return User()

else:
    # ---------- 真实模式：fastapi-users 栈 ----------
    # ---------- Real mode: fastapi-users stack ----------
    import uuid
    from typing import AsyncGenerator
    from fastapi_users import FastAPIUsers
    from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
    from sqlalchemy.ext.asyncio import AsyncSession

    from db.engine import async_session_maker          # CN: 异步会话工厂 / EN: async session factory
    from models.auth_user_real import UserTable        # CN: 真实用户表 / EN: real user table
    from models.auth_schemas import UserRead, UserCreate, UserUpdate  # Pydantic schemas

    async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session

    async def get_user_db(session: AsyncSession = Depends(get_async_session)):
        yield SQLAlchemyUserDatabase(session, UserTable)

    bearer_transport = BearerTransport(tokenUrl="/auth/jwt/login")

    def get_jwt_strategy() -> JWTStrategy:
        return JWTStrategy(
            secret=os.getenv("JWT_SECRET", "change-me"),
            lifetime_seconds=60 * 60 * 24
        )

    auth_backend = AuthenticationBackend(
        name="jwt",
        transport=bearer_transport,
        get_strategy=get_jwt_strategy
    )

    fastapi_users = FastAPIUsers[UserTable, uuid.UUID](get_user_db, [auth_backend])
    current_active_user = fastapi_users.current_user(active=True)
