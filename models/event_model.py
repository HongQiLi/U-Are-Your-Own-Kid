# models/event_model.py
# 每个日历事件归属一个用户（owner_id）
from sqlmodel import SQLModel, Field
import uuid

class Event(SQLModel, table=True):
    __tablename__ = "events"
    id: str = Field(primary_key=True)     # 由前端传 uuid
    title: str
    start: str                            # ISO 时间字符串
    end: str
    allDay: bool = False
    role: str = "child"                   # 可用于家长/孩子视图
    notes: str = ""
    owner_id: uuid.UUID                   # 归属用户（鉴权后自动写入）
