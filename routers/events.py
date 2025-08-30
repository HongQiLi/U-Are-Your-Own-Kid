# routers/events.py
# ===========================================================
# 日历事件路由（异步 DB + 用户鉴权 + 前后端字段映射）
# Calendar events router (async DB + auth + field mapping)
# ===========================================================

from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.session import get_session                         # ✅ 统一使用项目级异步会话依赖
from services.auth import current_active_user, User        # 鉴权依赖
from models.event_model import Event                       # 事件 ORM 模型

# 由外部聚合器统一加前缀 prefix="/events"
router = APIRouter(prefix="")

# -------------------- 请求体验证模型（前端视图） --------------------
class EventCreate(BaseModel):
    title: str
    start: datetime                # ISO 字符串会被自动解析
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

# -------------------- 映射工具 --------------------
def to_fc(e: Event) -> Dict[str, Any]:
    """ORM -> 前端：snake_case -> camelCase, datetime -> ISO"""
    return {
        "id": str(e.id),
        "owner_id": str(e.owner_id),
        "title": e.title,
        "start": e.start.isoformat(),
        "end": e.end.isoformat(),
        "allDay": bool(getattr(e, "all_day", False)),
        "notes": e.notes,
        "tags": e.tags,
        "priority": e.priority,
        "status": e.status,
    }

def from_fc(d: Dict[str, Any]) -> Dict[str, Any]:
    """前端 -> ORM：camelCase -> snake_case"""
    data = dict(d)
    if "allDay" in data:
        data["all_day"] = data.pop("allDay")
    return data

# -------------------- 列表（窗口重叠查询） --------------------
@router.get("", response_model=None)
async def list_events(
    start: Optional[datetime] = Query(None, description="可见窗口起点 / view window start"),
    end: Optional[datetime] = Query(None, description="可见窗口终点 / view window end"),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Event).where(Event.owner_id == user.id)
    # 返回“有重叠”的事件：ev.end > start AND ev.start < end
    if start and end:
        stmt = stmt.where(Event.end > start, Event.start < end)
    elif start:
        stmt = stmt.where(Event.end > start)
    elif end:
        stmt = stmt.where(Event.start < end)
    stmt = stmt.order_by(Event.start)

    rs = await session.execute(stmt)
    return [to_fc(e) for e in rs.scalars()]

# -------------------- 创建单条 --------------------
@router.post("", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_event(
    item: EventCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    data = from_fc(item.model_dump(exclude_unset=True))

    # 兜底：无 end 则默认 +1h；并做显式校验（与模型约束 end > start 保持一致）
    start = data.get("start")
    end = data.get("end") or (start + timedelta(hours=1) if start else None)

    if not start or not end:
        raise HTTPException(status_code=422, detail="start and end are required")

    if end <= start:
        raise HTTPException(status_code=422, detail="end must be after start")

    data["start"], data["end"] = start, end

    ev = Event(owner_id=user.id, **{k: v for k, v in data.items() if k in Event.model_fields})
    session.add(ev)
    await session.commit()
    await session.refresh(ev)
    return to_fc(ev)

# -------------------- 批量创建 --------------------
@router.post("/bulk", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_events_bulk(
    items: List[EventCreate],
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    created: list[Event] = []
    for it in items:
        data = from_fc(it.model_dump(exclude_unset=True))
        start = data.get("start")
        end = data.get("end") or (start + timedelta(hours=1) if start else None)

        if not start or not end or end <= start:
            # 简单起见：遇到非法条目直接 422；也可选择跳过并继续
            raise HTTPException(status_code=422, detail="Invalid time range in bulk item")

        data["start"], data["end"] = start, end

        ev = Event(owner_id=user.id, **{k: v for k, v in data.items() if k in Event.model_fields})
        session.add(ev)
        created.append(ev)

    await session.commit()
    for ev in created:
        await session.refresh(ev)
    return [to_fc(ev) for ev in created]

# -------------------- 查询单条 --------------------
@router.get("/{event_id}", response_model=None)
async def get_event(
    event_id: UUID,                                   # 直接用 UUID
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    ev = await session.get(Event, event_id)
    if not ev or ev.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Event not found")
    return to_fc(ev)

# -------------------- 部分更新（拖拽/拉伸） --------------------
@router.patch("/{event_id}", response_model=None)
async def update_event(
    event_id: UUID,                                   # 直接用 UUID
    patch: EventUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    rs = await session.execute(select(Event).where(Event.id == event_id, Event.owner_id == user.id))
    ev = rs.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    data = from_fc(patch.model_dump(exclude_unset=True))

    # 计算“更新后的”时间范围并校验
    new_start = data.get("start", ev.start)
    new_end = data.get("end", ev.end)
    if new_end <= new_start:
        raise HTTPException(status_code=422, detail="end must be after start")

    # 逐字段更新（只更新存在的字段）
    for k, v in data.items():
        if v is None:
            continue
        if k in Event.model_fields:
            setattr(ev, k, v)

    session.add(ev)
    await session.commit()
    await session.refresh(ev)
    return to_fc(ev)

# -------------------- 删除单条 --------------------
@router.delete("/{event_id}", response_model=None)
async def delete_event(
    event_id: UUID,                                   # 直接用 UUID
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    rs = await session.execute(select(Event).where(Event.id == event_id, Event.owner_id == user.id))
    ev = rs.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    await session.delete(ev)
    await session.commit()
    return {"deleted": str(event_id)}
