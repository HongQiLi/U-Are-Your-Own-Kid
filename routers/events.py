# routers/events.py
# ===========================================================
# 日历事件路由（异步 DB + 用户鉴权 + 前后端字段映射）
# Calendar events router (async DB + auth + field mapping)
# ===========================================================

from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.engine import async_session_maker                         # 异步会话工厂 / async session factory
from services.auth import current_active_user, User               # 鉴权依赖 / auth dependency
from models.event_model import Event                              # 事件 ORM 模型 / Event ORM model

# 你可以在这里就加前缀，也可以在 routers/__init__.py 里统一加
# You may set prefix here, or in routers/__init__.py aggregator.
router = APIRouter(prefix="")   # 为空表示由外部 include_router(prefix="/events") 统一加


# -------------------- 请求体验证模型（前端视图） / Request Schemas (frontend view) --------------------
# 让 Pydantic 自动把 ISO 字符串解析为 datetime，allDay 用前端风格命名
# Let Pydantic parse ISO into datetime; keep allDay (frontend naming)

class EventCreate(BaseModel):
    title: str
    start: datetime
    end: Optional[datetime] = None
    allDay: bool = False
    notes: Optional[str] = None
    tags: Optional[str] = None
    priority: Optional[int] = 0
    status: Optional[str] = "planned"

class EventUpdate(BaseModel):
    title: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    allDay: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None


# -------------------- 依赖：获取异步数据库会话 / Dependency: get async DB session --------------------
async def get_session():
    async with async_session_maker() as s:
        yield s


# -------------------- 映射工具 / Mapping helpers --------------------
def to_fc(e: Event) -> Dict[str, Any]:
    """把 ORM 对象映射为前端需要的格式（snake_case -> camelCase, datetime -> ISO）"""
    # 如果你的 Event 仍然是 allDay（而不是 all_day），这里也做了兼容
    all_day_val = getattr(e, "all_day", None)
    if all_day_val is None and hasattr(e, "allDay"):
        all_day_val = getattr(e, "allDay")

    return {
        "id": str(e.id),
        "owner_id": str(e.owner_id),
        "title": e.title,
        "start": e.start.isoformat(),
        "end": e.end.isoformat(),
        "allDay": bool(all_day_val),
        "notes": e.notes,
        "tags": e.tags,
        "priority": e.priority,
        "status": e.status,
    }

def from_fc(d: Dict[str, Any]) -> Dict[str, Any]:
    """把前端 JSON 映射为 ORM 字段（camelCase -> snake_case）"""
    data = dict(d)
    if "allDay" in data:
        data["all_day"] = data.pop("allDay")
    return data


# =============== 列表（支持可见时间窗，返回重叠的事件）/ List with overlapping window ===============
@router.get("", response_model=None)
async def list_events(
    # FullCalendar 会带 ?start=...&end=...（可选）。若未传，则返回该用户全部。
    # FullCalendar passes ?start=...&end=... (optional). If missing, return all.
    start: Optional[datetime] = Query(None, description="可见窗口起点 / view window start"),
    end: Optional[datetime] = Query(None, description="可见窗口终点 / view window end"),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    q = select(Event).where(Event.owner_id == user.id)

    # 如果提供了窗口，则返回“有重叠”的事件：ev.end > start AND ev.start < end
    # If window provided, return overlapping events: ev.end > start AND ev.start < end
    if start and end:
        q = q.where(Event.end > start, Event.start < end)
    elif start:
        q = q.where(Event.end > start)
    elif end:
        q = q.where(Event.start < end)

    q = q.order_by(Event.start)
    rs = await session.execute(q)
    items = list(rs.scalars())
    return [to_fc(e) for e in items]


# =============== 创建单条 / Create one ===============
@router.post("", response_model=None)
async def create_event(
    item: EventCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    data = from_fc(item.model_dump(exclude_unset=True))
    # 兜底：如果 end 为空，默认设为 start（或 start+1h，看产品需求）
    # Fallback: if end missing, set to start (or start+1h as you like)
    if data.get("end") is None and data.get("start") is not None:
        data["end"] = data["start"]  # 或者：data["end"] = data["start"] + timedelta(hours=1)

    obj = Event(owner_id=user.id, **{k: v for k, v in data.items() if k in Event.model_fields})
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return to_fc(obj)


# =============== 批量创建（AI 生成后一次性落库）/ Bulk create (AI batch) ===============
@router.post("/bulk", response_model=None)
async def create_events_bulk(
    items: List[EventCreate],
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    objs: List[Event] = []
    for it in items:
        data = from_fc(it.model_dump(exclude_unset=True))
        if data.get("end") is None and data.get("start") is not None:
            data["end"] = data["start"]
        ev = Event(owner_id=user.id, **{k: v for k, v in data.items() if k in Event.model_fields})
        session.add(ev)
        objs.append(ev)
    await session.commit()
    for o in objs:
        await session.refresh(o)
    return [to_fc(o) for o in objs]


# =============== 查询单条 / Retrieve one ===============
@router.get("/{event_id}", response_model=None)
async def get_event(
    event_id: str,                                           # 你的主键若为 UUID，这里也可以用 UUID
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    obj = await session.get(Event, event_id)
    if not obj or obj.owner_id != user.id:
        raise HTTPException(404, "Event not found")
    return to_fc(obj)


# =============== 部分更新（拖拽/拉伸）/ Partial update (drag/resize) ===============
@router.patch("/{event_id}", response_model=None)
async def update_event(
    event_id: str,
    patch: EventUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    rs = await session.execute(select(Event).where(Event.id == event_id, Event.owner_id == user.id))
    obj = rs.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Event not found")

    data = from_fc(patch.model_dump(exclude_unset=True))
    # 逐字段更新；忽略 None；仅更新模型中存在的字段
    for k, v in data.items():
        if v is None:
            continue
        if k in Event.model_fields:
            setattr(obj, k, v)

    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return to_fc(obj)


# =============== 删除单条 / Delete one ===============
@router.delete("/{event_id}", response_model=None)
async def delete_event(
    event_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    rs = await session.execute(select(Event).where(Event.id == event_id, Event.owner_id == user.id))
    obj = rs.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Event not found")
    await session.delete(obj)
    await session.commit()
    return {"deleted": str(event_id)}
