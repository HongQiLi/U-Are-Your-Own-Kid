# routers/parent.py
# 家长模式模块 / Parent Mode: View child tasks and provide suggestions

from fastapi import APIRouter, HTTPException  # 引入 FastAPI 工具 / Import FastAPI router and error handling
from pydantic import BaseModel  # 用于数据模型校验 / For request body validation
from typing import List, Dict
import json
import os

router = APIRouter()

# =====================
#  文件路径配置 / File-based mock DB
# =====================
DATA_DIR = "data"
BIND_FILE = os.path.join(DATA_DIR, "parent_child_map.json")
TASK_FILE = os.path.join(DATA_DIR, "child_task_store.json")
SUGGEST_FILE = os.path.join(DATA_DIR, "parent_suggestions.json")

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
#   模型定义 / Models
# =====================

class ParentLinkRequest(BaseModel):
    parent_id: str  # 家长ID / Parent ID
    child_id: str   # 孩子ID / Child ID

class Suggestion(BaseModel):
    parent_id: str  # 家长ID / Parent ID
    child_id: str   # 孩子ID / Child ID
    text: str       # 建议内容 / Suggestion or encouragement

# ========================
#     家长绑定孩子接口
# ========================

@router.post("/parent/bind")
def bind_child(parent_link: ParentLinkRequest):
    """
    家长绑定孩子账户 / Bind a parent to a child account
    """
    parent_child_map = load_json(BIND_FILE)
    if parent_link.parent_id not in parent_child_map:
        parent_child_map[parent_link.parent_id] = []

    if parent_link.child_id not in parent_child_map[parent_link.parent_id]:
        parent_child_map[parent_link.parent_id].append(parent_link.child_id)
        save_json(BIND_FILE, parent_child_map)
        return {"message": "Parent successfully linked to child."}
    else:
        return {"message": "Parent already linked to child."}

# ========================
#      查看孩子任务接口
# ========================

@router.get("/parent/{parent_id}/child-tasks")
def view_children_tasks(parent_id: str) -> Dict[str, List[Dict]]:
    """
    获取家长绑定孩子的所有任务 / Get all tasks of children linked to this parent
    """
    parent_child_map = load_json(BIND_FILE)
    child_task_store = load_json(TASK_FILE)

    children = parent_child_map.get(parent_id, [])
    tasks = {child_id: child_task_store.get(child_id, []) for child_id in children}
    return tasks

# ========================
#     家长提交建议接口
# ========================

@router.post("/parent/suggest")
def submit_suggestion(suggestion: Suggestion):
    """
    家长提交建议或鼓励语 / Submit a suggestion or encouragement from parent to child
    """
    parent_suggestions = load_json(SUGGEST_FILE)

    if suggestion.child_id not in parent_suggestions:
        parent_suggestions[suggestion.child_id] = []

    parent_suggestions[suggestion.child_id].append({
        "from": suggestion.parent_id,
        "text": suggestion.text
    })

    save_json(SUGGEST_FILE, parent_suggestions)
    return {"message": "Suggestion submitted successfully."}

# ========================
#     查看建议列表接口
# ========================

@router.get("/parent/{child_id}/suggestions")
def get_suggestions(child_id: str):
    """
    查看对某个孩子的所有建议 / Get all parent suggestions for a specific child
    """
    parent_suggestions = load_json(SUGGEST_FILE)
    return parent_suggestions.get(child_id, [])

# ========================
#  推荐计划接口（模拟推荐引擎）
# ========================

@router.get("/parent/{child_id}/view_child_plan")
def view_child_plan(child_id: str):
    """
    模拟返回推荐计划 / Simulate a child plan based on survey or tasks
    """
    child_task_store = load_json(TASK_FILE)
    past_tasks = child_task_store.get(child_id, [])

    # 简单推荐逻辑：如果有阅读任务就推荐写作 / Recommend writing if reading was done
    suggestions = []
    for task in past_tasks:
        if "reading" in task.get("name", "").lower():
            suggestions.append("Try writing a summary of what you read!")

    # 如果没有任务历史就推荐开始学习计划 / Recommend general study plan if empty
    if not suggestions:
        suggestions.append("Start with 15 minutes of focused reading each day.")

    return {
        "child_id": child_id,
        "recommendations": suggestions
    }
