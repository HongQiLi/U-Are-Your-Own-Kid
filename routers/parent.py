# routers/parent.py
# Parent Mode: View child tasks and offer suggestions

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

# 模拟数据库结构 / Simulated in-memory DBs
parent_child_map = {}      # e.g., {"parent_1": ["child_1", "child_2"]}
child_task_store = {}      # e.g., {"child_1": [{"name": "Reading", "status": "completed"}]}
parent_suggestions = {}    # e.g., {"child_1": [{"from": "parent_1", "text": "Great job!"}]}

# 家长绑定孩子 / Parent binds to child
class ParentLinkRequest(BaseModel):
    parent_id: str
    child_id: str

@router.post("/parent/bind")
def bind_child(parent_link: ParentLinkRequest):
    """
    Bind a parent to a child account.
    """
    if parent_link.parent_id not in parent_child_map:
        parent_child_map[parent_link.parent_id] = []

    if parent_link.child_id not in parent_child_map[parent_link.parent_id]:
        parent_child_map[parent_link.parent_id].append(parent_link.child_id)
        return {"message": "Parent successfully linked to child."}
    else:
        return {"message": "Parent already linked to child."}


# 查看孩子的任务情况 / View child tasks
@router.get("/parent/{parent_id}/child-tasks")
def view_children_tasks(parent_id: str) -> Dict[str, List[Dict]]:
    """
    Get all tasks of children linked to this parent.
    """
    children = parent_child_map.get(parent_id, [])
    tasks = {child_id: child_task_store.get(child_id, []) for child_id in children}
    return tasks


# 家长给任务建议 / Parent provides feedback or encouragement
class Suggestion(BaseModel):
    parent_id: str
    child_id: str
    text: str

@router.post("/parent/suggest")
def submit_suggestion(suggestion: Suggestion):
    """
    Submit a suggestion or encouragement from parent to child.
    """
    if suggestion.child_id not in parent_suggestions:
        parent_suggestions[suggestion.child_id] = []

    parent_suggestions[suggestion.child_id].append({
        "from": suggestion.parent_id,
        "text": suggestion.text
    })
    return {"message": "Suggestion submitted successfully."}


# 查看家长对孩子的建议 / View suggestions made to a child
@router.get("/parent/{child_id}/suggestions")
def get_suggestions(child_id: str):
    """
    Get all parent suggestions for a specific child.
    """
    return parent_suggestions.get(child_id, [])
