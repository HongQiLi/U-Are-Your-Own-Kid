# models/event_model.py
from sqlmodel import SQLModel, Field
import uuid

class Event(SQLModel, table=True):
    __tablename__ = "events"
    id: str = Field(primary_key=True)
    title: str
    start: str
    end: str
    allDay: bool = False
    role: str = "child"
    notes: str = ""
    owner_id: uuid.UUID                 # 记录属于哪个用户
