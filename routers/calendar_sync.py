# routers/calendar_sync.py
# 日历同步模块（合并版）/ Calendar Sync (merged)
# 目标：
# 1) 导入外部日历事件并同步为孩子任务
# 2) 支持查看与更新外部导入的事件
# 3) 保存 FullCalendar 的当前事件列表（前端拖拽后的整表）
# 存储：全部使用 data/*.json 文件持久化，便于调试与部署

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
import os
import json


router = APIRouter()

# ========== 路径与文件 / Paths & files ==========
DATA_DIR = "data"
EXTERNAL_FILE = os.path.join(DATA_DIR, "external_calendar.json")       # 外部日历日志 / external calendar log
TASK_FILE = os.path.join(DATA_DIR, "child_task_store.json")            # 孩子任务仓库 / child task store
SAVED_FILE = os.path.join(DATA_DIR, "saved_calendar_events.json")      # FullCalendar 事件快照 / saved fullcalendar events

# 确保 data 目录存在 / ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# ========== 工具函数 / Helpers ==========
def load_json(filepath):
    """ 从 JSON 文件加载数据（若不存在或损坏返回空结构）
        Load dict/list from JSON file; return empty structure if missing/bad. """
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_json(filepath, data):
    """ 保存数据到 JSON 文件（utf-8，缩进便于查看）
        Save data to JSON file with utf-8 and pretty indent. """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== 数据模型 / Schemas ==========
class CalendarEvent(BaseModel):
    # 导入外部事件时用的精简模型 / Minimal model for external import
    child_id: str              # 孩子ID / child id
    event_title: str           # 事件标题 / event title
    duration_minutes: int      # 持续分钟 / duration in minutes

class EventIn(BaseModel):
    # FullCalendar 保存时用的事件结构 / Event model for FullCalendar snapshot
    title: str                 # 标题 / event title
    start: str                 # 开始时间 ISO 字符串 / ISO start
    end: Optional[str] = None  # 结束时间 ISO 字符串 / ISO end (optional)
    extendedProps: Optional[dict] = None  # 自定义属性 / custom meta

# ========== 1) 导入外部日历 → 同步为任务 / Import external calendar → sync to child tasks ==========
@router.post("/import")
def import_calendar_event(event: CalendarEvent):
    """
    导入外部日历任务到孩子任务列表中（写 external_calendar.json 与 child_task_store.json）
    Import external calendar event and sync into child's task list.
    """
    external_calendar = load_json(EXTERNAL_FILE)  # dict: child_id -> [ {title, duration}, ... ]
    child_task_store = load_json(TASK_FILE)       # dict: child_id -> [ {name, duration, ...}, ... ]

    # 1) 记录一条外部日历事件 / append one external calendar event
    external_calendar.setdefault(event.child_id, []).append({
        "title": event.event_title,
        "duration": event.duration_minutes
    })
    save_json(EXTERNAL_FILE, external_calendar)

    # 2) 同步为一个孩子任务（来源标记为 calendar）/ sync into child's task store
    child_task_store.setdefault(event.child_id, []).append({
        "name": event.event_title,
        "duration": event.duration_minutes,
        "source": "calendar",
        "status": "pending"
    })
    save_json(TASK_FILE, child_task_store)

    return {"message": "Event imported and synced to child task list."}

# ========== 2) 查看外部导入日志 / View external import log ==========
@router.get("/{child_id}/log")
def view_calendar_log(child_id: str):
    """
    查看某个孩子的外部日历记录（来自 external_calendar.json）
    View imported external calendar events for a child.
    """
    external_calendar = load_json(EXTERNAL_FILE)
    return external_calendar.get(child_id, [])

# ========== 3) 更新外部导入事件（拖拽后重命名/改时长）/ Update imported event ==========
@router.put("/{child_id}/update")
def update_calendar_event(
    child_id: str,
    old_title: str = Body(..., embed=True, description="原任务名称 / old task title"),
    new_title: str = Body(..., embed=True, description="新任务名称 / new task title"),
    new_duration: int = Body(..., embed=True, description="新任务时长（分钟）/ new duration in minutes")
):
    """
    拖拽或编辑后更新外部导入任务，同时更新 external_calendar.json 与 child_task_store.json
    Update an imported event and its synced child task.
    """
    external_calendar = load_json(EXTERNAL_FILE)
    child_task_store = load_json(TASK_FILE)

    found = False

    # 更新外部日历记录 / update external log
    for evt in external_calendar.get(child_id, []):
        if evt.get("title") == old_title:
            evt["title"] = new_title
            evt["duration"] = new_duration
            found = True
            break

    # 更新孩子任务仓库（同名匹配）/ update task store
    for task in child_task_store.get(child_id, []):
        if task.get("name") == old_title:
            task["name"] = new_title
            task["duration"] = new_duration
            break

    if not found:
        raise HTTPException(status_code=404, detail="Event not found.")

    save_json(EXTERNAL_FILE, external_calendar)
    save_json(TASK_FILE, child_task_store)

    return {"message": "Event updated successfully."}

# ========== 4) 保存 FullCalendar 当前全部事件 / Save full calendar snapshot ==========
@router.post("/save")
def save_calendar(events: List[EventIn]):
    """
    保存前端 FullCalendar 的当前事件列表（覆盖式保存）
    Save current FullCalendar events (overwrite snapshot).
    前端：calendar.getEvents() → 映射为 EventIn 列表后提交
    """
    # Pydantic 模型转可序列化 dict / Pydantic models to plain dicts
    serializable = [e.model_dump() for e in events]
    save_json(SAVED_FILE, serializable)
    return {"message": "saved", "count": len(serializable)}

# ========== 5) 调试：查看已保存的 FullCalendar 事件 / Dump saved ==========
@router.get("/dump")
def dump_calendar():
    """
    查看已保存的 FullCalendar 事件清单（来自 saved_calendar_events.json）
    Debug: view saved FullCalendar events list.
    """
    data = load_json(SAVED_FILE)
    # 若文件为空或不是列表，统一返回空列表 / normalize to list
    return data if isinstance(data, list) else []
