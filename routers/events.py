# routers/events.py
# ===========================================================
# 日历事件路由（数据库持久化 + 用户鉴权）
# Calendar events router (DB persistence + user-level auth)
# ===========================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import async_session_maker                      # 数据库会话 / DB session
from services.auth import current_active_user, User            # 鉴权与用户类型 / Auth & user type
from models.event_model import Event                           # 事件表模型 / Event table

router = APIRouter()  # 注意：不在这里设置前缀；在 routers/__init__.py 统一用 prefix="/events"
                      # Note: no prefix here; use prefix="/events" in routers/__init__.py


# ---------- Pydantic 请求体模型（避免要求客户端传 id/owner_id） ----------
# ---------- Pydantic request schemas (so client needn't send id/owner_id) ----------
class EventCreate(BaseModel):
    title: str
    start: str
    end: Optional[str] = None
    allDay: bool = False

class EventUpdate(BaseModel):
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    allDay: Optional[bool] = None


# 依赖：获取一个数据库会话 / Dependency: provide a DB session
async def get_session():
    async with async_session_maker() as s:
        yield s


# =============== 列表（支持时间窗过滤）/ List with time window filter ===============
@router.get("", response_model=List[Event])
async def list_events(
    # FullCalendar 会带 ?start=...&end=...；这里两者可选，未传则返回该用户全部
    # FullCalendar queries ?start=...&end=...; optional here
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    q = select(Event).where(Event.owner_id == user.id)
    if start:
        q = q.where(Event.start >= start)   # 假设 Event.start 为 ISO 字符串；若为 datetime 更佳
    if end:
        q = q.where(Event.start <= end)
    rs = await session.execute(q)
    return list(rs.scalars())


# =============== 创建单条 / Create one ===============
@router.post("", response_model=Event)
async def create_event(
    item: EventCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    obj = Event(
        title=item.title,
        start=item.start,
        end=item.end,
        allDay=item.allDay,
        owner_id=user.id,     # 绑定到当前用户 / stamp owner
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


# =============== 批量创建（AI 生成后一次性落库）/ Bulk create (for AI batch) ===============
@router.post("/bulk", response_model=List[Event])
async def create_events_bulk(
    items: List[EventCreate],
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    objs: List[Event] = []
    for it in items:
        ev = Event(
            title=it.title,
            start=it.start,
            end=it.end,
            allDay=it.allDay,
            owner_id=user.id,
        )
        session.add(ev)
        objs.append(ev)
    await session.commit()
    # 刷新每个对象拿到 id / refresh to get IDs
    for o in objs:
        await session.refresh(o)
    return objs


# =============== 更新单条（拖拽/拉伸）/ Update one (drag/resize) ===============
@router.put("/{event_id}", response_model=Event)
async def update_event(
    event_id: str,
    patch: EventUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    rs = await session.execute(
        select(Event).where(Event.id == event_id, Event.owner_id == user.id)
    )
    obj = rs.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Not found")

    data = patch.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)

    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


# =============== 删除单条 / Delete one ===============
@router.delete("/{event_id}")
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
