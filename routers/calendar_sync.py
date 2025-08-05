# routers/calendar_sync.py
# 日历同步模块 / Calendar Sync: Import tasks from external calendar (e.g., Google Calendar)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import json
import os

router = APIRouter()

# =====================
#  文件路径配置 / File-based mock DB
# =====================
DATA_DIR = "data"
CALENDAR_FILE = os.path.join(DATA_DIR, "external_calendar.json")
TASK_FILE = os.path.join(DATA_DIR, "child_task_store.json")

# 初始化数据文件夹 / Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# 加载JSON文件 / Load or initialize empty JSON data

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

# 保存JSON数据 / Save JSON data to file

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

# =====================
#  数据模型定义 / Models
# =====================

class CalendarEvent(BaseModel):
    child_id: str            # 孩子ID / Child ID
    event_title: str         # 日历事件标题 / Event title
    duration_minutes: int    # 持续时长（分钟）/ Duration in minutes

# =====================
#  导入外部日历事件接口 / Import calendar events to child's task
# =====================

@router.post("/calendar/import")
def import_calendar_event(event: CalendarEvent):
    """
    导入外部日历任务到孩子任务列表中 / Import external calendar events as child tasks
    """
    external_calendar = load_json(CALENDAR_FILE)
    child_task_store = load_json(TASK_FILE)

    # 保存事件到外部日历记录 / Save raw calendar event
    external_calendar.setdefault(event.child_id, []).append({
        "title": event.event_title,
        "duration": event.duration_minutes
    })
    save_json(CALENDAR_FILE, external_calendar)

    # 同步任务到任务列表 / Sync into child's task store
    child_task_store.setdefault(event.child_id, []).append({
        "name": event.event_title,
        "duration": event.duration_minutes,
        "source": "calendar",
        "status": "pending"
    })
    save_json(TASK_FILE, child_task_store)

    return {"message": "Event imported and synced to child task list."}

# =====================
#  查看外部日历记录接口 / View external calendar log
# =====================

@router.get("/calendar/{child_id}/log")
def view_calendar_log(child_id: str):
    """
    查看某个孩子的外部日历记录 / View imported external calendar events
    """
    external_calendar = load_json(CALENDAR_FILE)
    return external_calendar.get(child_id, [])

from fastapi import Body

# =====================
#  拖拽更新任务接口 / Update calendar event timing (e.g., after dragging in UI)
# =====================

@router.put("/calendar/{child_id}/update")
def update_calendar_event(
    child_id: str,
    old_title: str = Body(..., embed=True, description="原任务名称 / Old task name"),
    new_title: str = Body(..., embed=True, description="新任务名称 / New task name"),
    new_duration: int = Body(..., embed=True, description="新任务时长 / New task duration (minutes)")
):
    """
    拖拽后更新日历任务 / Update a previously imported calendar task
    """
    external_calendar = load_json(CALENDAR_FILE)
    child_task_store = load_json(TASK_FILE)

    found = False

    # 更新外部日历记录 / Update external calendar
    for evt in external_calendar.get(child_id, []):
        if evt["title"] == old_title:
            evt["title"] = new_title
            evt["duration"] = new_duration
            found = True
            break

    # 更新同步任务列表 / Update synced child task
    for task in child_task_store.get(child_id, []):
        if task["name"] == old_title:
            task["name"] = new_title
            task["duration"] = new_duration
            break

    if not found:
        raise HTTPException(status_code=404, detail="Event not found.")

    save_json(CALENDAR_FILE, external_calendar)
    save_json(TASK_FILE, child_task_store)

    return {"message": "Event updated successfully."}

