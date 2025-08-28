# models/auth_user.py
# -----------------------------------------------------------------------------
# 用户模型（数据库表）+ 接口用的 Pydantic Schemas（输入/输出）
# User DB model + Pydantic schemas for API (request/response)
# -----------------------------------------------------------------------------
# 设计要点 / Design notes
# - 继承 fastapi-users 的 SQLAlchemyBaseUserTableUUID，这个基类已经包含：
#   id(UUID 主键)、email、hashed_password、is_active、is_superuser、is_verified
#   The base class already defines id/email/hashed_password/is_active/is_superuser/is_verified.
# - 在此模型上按业务需要增加字段（role/nickname/timezone/locale）。
#   We extend business fields on top (role/nickname/timezone/locale).
# - 下方的 UserRead/UserCreate/UserUpdate 是接口层的数据契约（不建表）。
#   The schemas below are API contracts only (no tables are created for them).
# -----------------------------------------------------------------------------

from typing import Optional
import uuid

from sqlmodel import SQLModel, Field
from fastapi_users import schemas
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID


# === 数据库表：用户（用于注册/登录）===
# === Database table: User (for sign-up/sign-in) ===
class User(SQLModel, SQLAlchemyBaseUserTableUUID, table=True):
    __tablename__ = "users"  # 外键会写成 foreign_key="users.id"；固定表名更稳
                             # Foreign keys will reference "users.id"; keep this stable.

    # 业务角色：parent/child（先用字符串，后续需要可加校验或枚举）
    # Business role: "parent" | "child" (string now; can enforce enum/validation later)
    role: str = Field(default="parent", description="用户角色/Role: parent or child")

    # 昵称（显示名，可选）
    # Display nickname (optional)
    nickname: Optional[str] = Field(default=None, description="昵称/Nickname")

    # 时区（用于事件显示/提醒等；默认 America/Denver）
    # Timezone for rendering events/reminders; default America/Denver
    timezone: str = Field(default="America/Denver", description="时区/Timezone")

    # 界面语言（国际化：en/zh 等）
    # UI locale for i18n (e.g., en/zh)
    locale: str = Field(default="en", description="语言/Locale")


# === 接口响应模型：返回给前端看的安全字段（不包含密码哈希）===
# === API response schema: safe fields for client (no password hash) ===
class UserRead(schemas.BaseUser[uuid.UUID]):
    # 继承自 fastapi-users 的 BaseUser[UUID] 已含：
    # id/email/is_active/is_superuser/is_verified
    # BaseUser[UUID] includes: id/email/is_active/is_superuser/is_verified
    role: str
    nickname: Optional[str] = None
    timezone: str
    locale: str


# === 接口请求模型（注册）：前端提交的字段（包含明文 password）===
# === API request schema (sign-up): fields client submits (includes plain password) ===
class UserCreate(schemas.BaseUserCreate):
    # BaseUserCreate 已包含：email、password
    # BaseUserCreate includes: email, password
    role: str = "parent"
    nickname: Optional[str] = None
    timezone: str = "America/Denver"
    locale: str = "en"


# === 接口请求模型（更新）：部分字段可选更新（不需要全量覆盖）===
# === API request schema (partial update): optional fields, no full overwrite ===
class UserUpdate(schemas.BaseUserUpdate):
    # BaseUserUpdate 已包含：email（可选）、password（可选，用于改密）
    # BaseUserUpdate includes optional email/password for profile/password change
    role: Optional[str] = None
    nickname: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
