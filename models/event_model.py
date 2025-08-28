# models/event_model.py
# -----------------------------------------------------------------------------
# 事件表（数据库模型）/ Event DB Model (SQLModel table)
# -----------------------------------------------------------------------------
# 设计要点 / Design notes
# - 在数据库里用强类型 datetime 存储 start/end，排序与时间窗查询更稳定；
#   Use strong-typed datetime for start/end in DB for better sorting & range filtering.
# - 主键使用 UUID，后端默认生成；如果前端传入字符串 UUID，也可被解析。
#   Use UUID as primary key; server generates by default. Client-provided UUID string is acceptable.
# - 这里不做字段别名，保持后端内部 snake_case（all_day）。
#   No alias here; keep snake_case internally (all_day). We'll map to allDay in the router.

from __future__ import annotations
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class Event(SQLModel, table=True):
    __tablename__ = "events"

    # 主键 / Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # 归属用户（外键到 users.id）/ Owner foreign key -> users.id
    owner_id: UUID = Field(foreign_key="users.id", index=True)

    # 基本信息 / Core fields
    title: str
    start: datetime
    end: datetime
    all_day: bool = False

    # 可选信息 / Optional metadata
    notes: Optional[str] = None
    tags: Optional[str] = None          # MVP：逗号分隔字符串 / comma-separated tags (MVP)
    priority: int = 0
    status: str = "planned"
