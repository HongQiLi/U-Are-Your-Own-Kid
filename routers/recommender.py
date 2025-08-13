# routers/recommender.py
# 推荐系统路由 / Recommender API Router

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from models.user_profile import UserProfile          # 用户画像 / user profile schema
from models.task_model import Task                 # 任务模型 / task schema
from recommender.core import recommend_tasks       # 核心推荐逻辑 / core recommender

from typing import Literal
from fastapi import Query
from utils.openai_client import suggest_activities_with_openai
from utils.cohere_client import suggest_activities_with_cohere
from utils.hf_client import suggest_activities_with_hf

# 只创建一个路由器实例；不要重复定义，否则会覆盖之前注册的接口
# Create a single APIRouter instance. Do NOT redefine it later in the file.
router = APIRouter()

# ============= 接口一：主推荐 =============
# POST /recommend/tasks
# 说明：基于用户画像生成推荐任务（调用核心引擎）
# Desc: Generate recommended tasks via core engine based on user profile
@router.post("/tasks", response_model=List[Task])
async def get_recommended_tasks(user_profile: UserProfile):
    """
    输入 / Input:
        UserProfile: 包含兴趣问卷、可用时间等 / includes survey, availability, etc.
    输出 / Output:
        List[Task]: 推荐的任务列表 / list of recommended tasks
    注意 / Note:
        本接口路径不要再包含 'recommend'，因为 main.py 已经用 prefix="/recommend" 挂载
        Do not put 'recommend' in the decorator path; main.py mounts with prefix="/recommend".
    """
    try:
        tasks = await recommend_tasks(user_profile)
        return tasks
    except Exception as e:
        # 捕获并抛出 500，便于前端定位 / raise 500 for frontend debugging
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")


# ============= 接口二：轻量推荐（给前端拖拽用） =============
# POST /recommend/tasks-lite
# 说明：根据兴趣与可用时段，生成简化任务卡片，便于前端渲染和拖拽
# Desc: Simple rule-based tasks for UI drag-and-drop
class LiteReq(BaseModel):
    # 用户兴趣，例如 ["写作","篮球"] / user interests
    interests: List[str] = []
    # 可用时段，例如 ["周一 16:00-17:00","周六 09:00-11:00"] / availability strings
    availability: List[str] = []

class LiteTask(BaseModel):
    # 标题 / title shown on the card
    title: str
    # 预计时长（分钟）/ duration in minutes
    duration: int
    # 标签（如 skill/reading）/ tag
    tag: str
    # 解释理由 / reason for recommendation
    reason: str

@router.post("/tasks-lite", response_model=List[LiteTask])
async def tasks_lite(req: LiteReq):
    """
    规则（简版）/ Simple rules:
      1) 每个兴趣映射两条活动：技能训练 + 阅读巩固
      2) 若提供可用时段，则默认给更长时长（60 分钟），否则 45 分钟
      3) 前端将这些项渲染为“可拖拽卡片”，拖入 FullCalendar

    输入示例 / Example input:
      {
        "interests": ["写作", "编程"],
        "availability": ["周一 16:00-17:00", "周六 09:00-11:00"]
      }
    """
    out: List[LiteTask] = []

    # 基础映射 / basic mapping for demo
    base_map = {
        "写作": [("写作练习", "skill"), ("阅读名家短篇", "reading")],
        "篮球": [("运球与投篮训练", "skill"), ("战术视频学习", "reading")],
        "编程": [("刷题与小练习", "skill"), ("阅读项目源码", "reading")],
    }

    # 兜底映射 / fallback when no known interests
    fallback = [("通用学习任务", "skill"), ("通用阅读计划", "reading")]

    # 根据是否有可用时段调整时长 / adjust duration by availability
    default_duration = 60 if req.availability else 45

    interests = req.interests or ["通用"]
    for interest in interests:
        pairs = base_map.get(interest, fallback)
        for name, tag in pairs:
            out.append(LiteTask(
                title=f"{interest}-{name}",
                duration=default_duration,
                tag=tag,
                reason=f"结合你的兴趣「{interest}」与作息，先安排{tag}训练与阅读巩固。"
            ))
    return out

# ============= 接口三：AI 直产活动条（统一结构，前端直接拖拽） =============
# GET /recommend/ai-suggest?q=...&provider=openai|cohere|hf
# 说明：调用指定大模型，返回 [{title, duration, tag, reason}] 统一结构
@router.get("/ai-suggest")
def ai_suggest(
    q: str = Query(..., description="用户自然语言需求 / user prompt"),
    provider: Literal["openai", "cohere", "hf"] = Query("openai")
):
    """
    返回统一结构的活动条：
    [{title, duration(分钟), tag(skill|reading|sport|social|art), reason}]
    """
    if provider == "openai":
        data = suggest_activities_with_openai(q)
    elif provider == "cohere":
        data = suggest_activities_with_cohere(q)
    else:
        data = suggest_activities_with_hf(q)

    # 兜底，确保字段完整，避免前端渲染报错
    out = []
    for x in (data or []):
        out.append({
            "title": str(x.get("title", "Untitled"))[:60],
            "duration": int(x.get("duration", 45)),
            "tag": x.get("tag", "skill"),
            "reason": str(x.get("reason", ""))
        })
    return out

