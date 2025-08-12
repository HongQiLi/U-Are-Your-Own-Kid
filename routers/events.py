# routers/events.py
# ===========================================================
# 日历事件路由（数据库持久化 + 用户鉴权）
# Calendar events router (DB persistence + user-level auth)
# ===========================================================

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import async_session_maker                  # 数据库会话 / DB session
from services.auth import current_active_user              # 鉴权 / Auth
from models.auth_user import User                          # 登录用户模型 / User model
from models.event_model import Event                       # 事件模型 / Event table

router = APIRouter()

# 依赖：获取一个数据库会话 / Dependency: provide a DB session
async def get_session():
    async with async_session_maker() as s:
        yield s

# 读取当前用户的全部事件 / List all events for current user
@router.get("/events", response_model=List[Event])
async def list_events(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    rs = await session.execute(select(Event).where(Event.owner_id == user.id))
    return list(rs.scalars())

# 批量创建事件（AI 生成后一次性落库）
# Bulk-create events (after AI generation)
@router.post("/events/bulk", response_model=List[Event])
async def create_events_bulk(
    items: List[Event],
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    for ev in items:
        ev.owner_id = user.id        # 归属当前用户 / stamp owner
        session.add(ev)
    await session.commit()

    # 简单起见：提交后重新查询并返回该用户全部事件
    # Simplicity: return all events of the user after commit
    rs = await session.execute(select(Event).where(Event.owner_id == user.id))
    return list(rs.scalars())

# 删除单个事件 / Delete one event
@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    rs = await session.execute(
        select(Event).where(Event.id == event_id, Event.owner_id == user.id)
    )
    obj = rs.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Not found")
    await session.delete(obj)
    await session.commit()
    return {"deleted": event_id}
