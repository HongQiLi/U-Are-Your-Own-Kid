# models/schedule_model.py
from sqlmodel import SQLModel, Field, Column, JSON
import uuid
from typing import Dict, Optional

class Schedule(SQLModel, table=True):
    __tablename__ = "schedules"
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: uuid.UUID                                           #  归属用户
    availability: Dict[str, int] = Field(sa_column=Column(JSON))  #  存 JSON

