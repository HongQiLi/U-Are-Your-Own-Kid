# models/event_model.py
# -----------------------------------------------------------------------------
# 事件表（数据库模型）/ Event DB Model (SQLModel table)
# -----------------------------------------------------------------------------
# 设计要点 / Design notes
# - 使用 UUID 主键（后端生成）；Use UUID PK generated on server
# - start/end 用 datetime，数据库层有校验 end > start；Strong-typed with DB check
# - 内部字段保持 snake_case（all_day）；路由会映射到 allDay 给前端
# - 为典型查询增加索引 (owner_id, start)；Add (owner_id, start) index
# - 记录 created_at/updated_at（UTC）；Keep audit timestamps (UTC)

from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import CheckConstraint, Index, func

def utcnow() -> datetime:
    # 统一使用带 tz 的 UTC 时间 / timezone-aware UTC
    return datetime.now(timezone.utc)

class Event(SQLModel, table=True):
    __tablename__ = "events"

    # 数据库层校验与索引 / DB-level constraints & indexes
    __table_args__ = (
        CheckConstraint("end > start", name="ck_events_end_gt_start"),  # 保证结束晚于开始
        Index("ix_events_owner_start", "owner_id", "start"),            # 常用查询加速
    )

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

    # 审计时间 / Audit timestamps (UTC)
    created_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": func.now()},  # DB 默认值（不同库精度略有差异）
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": func.now()},        # 每次更新由 DB/ORM 刷新
    )
