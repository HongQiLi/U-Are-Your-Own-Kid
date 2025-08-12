# models/auth_user.py

from typing import Optional
from sqlmodel import SQLModel, Field
from fastapi_users import schemas
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
import uuid

# === 数据库表：用户账号（用于注册/登录） ===
class User(SQLModel, SQLAlchemyBaseUserTableUUID, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # SQLAlchemyBaseUserTableUUID 已含: email, hashed_password, is_active, is_superuser, is_verified
    # 自定义业务字段：
    role: str = "parent"     # "parent" | "child"
    nickname: Optional[str] = None

    # 也可以预留一个 JSON 字段存画像（以后再加）：
    # profile_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))

# === Pydantic Schemas：用于 API 输入/输出 ===
class UserRead(schemas.BaseUser[uuid.UUID]):
    role: str
    nickname: Optional[str] = None

class UserCreate(schemas.BaseUserCreate):
    role: str = "parent"
    nickname: Optional[str] = None

class UserUpdate(schemas.BaseUserUpdate):
    role: Optional[str] = None
    nickname: Optional[str] = None
