# utils/openai_client.py
# OpenAI 客户端（SDK v1 写法），统一输出短文本建议列表

import os
from typing import List
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def generate_openai_reply(prompt: str) -> str:
    """
    返回一段纯文本（用于展示/调试）
    """
    if not client:
        return "OpenAI not configured: missing OPENAI_API_KEY"

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.7,
        max_tokens=300
    )
    return resp.choices[0].message.content.strip()

def suggest_activities_with_openai(prompt: str) -> List[dict]:
    """
    让模型输出 JSON 风格的活动建议（title/duration/tag）
    返回：[{title, duration, tag, reason}, ...]
    """
    if not client:
        return []

    sys = (
        "You are an assistant that outputs kid-friendly activity suggestions. "
        "Return 3-5 items as JSON array with fields: title (string), duration (int, minutes), "
        "tag (one of skill, reading, sport, social, art), reason (string). No extra text."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":sys},{"role":"user","content":prompt}],
        temperature=0.6,
        max_tokens=400
    )
    text = resp.choices[0].message.content.strip()

    # 简单兜底解析：如果不是严格 JSON，就包一层
    import json
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        # 解析失败时，退化为单条建议
        return [{"title": text[:40], "duration": 45, "tag": "skill", "reason": "AI free-form response"}]
