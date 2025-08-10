# utils/cohere_client.py
# Cohere 客户端。不同版本的 SDK 有 chat / generate 差异，这里做双分支兜底。

import os
from typing import List
import cohere

api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(api_key) if api_key else None

def generate_cohere_reply(prompt: str) -> str:
    if not co:
        return "Cohere not configured: missing COHERE_API_KEY"
    # 优先尝试 chat（新版本）
    try:
        r = co.chat(model="command-r", messages=[{"role":"user","content":prompt}])
        return (r.output_text or "").strip()
    except TypeError:
        # 旧版本只支持 generate
        r = co.generate(prompt=prompt, max_tokens=200, temperature=0.6, model="command")
        return r.generations[0].text.strip()

def suggest_activities_with_cohere(prompt: str) -> List[dict]:
    if not co:
        return []
    sys = (
        "You output a JSON array of 3 concise activity ideas for kids. "
        "Fields: title (string), duration (int minutes), tag (skill|reading|sport|social|art), reason (string)."
    )
    try:
        r = co.chat(
            model="command-r",
            messages=[{"role":"system","content":sys},{"role":"user","content":prompt}],
            temperature=0.6
        )
        text = (r.output_text or "").strip()
    except TypeError:
        # 旧 SDK 走 generate
        r = co.generate(prompt=sys + "\nUser:" + prompt, max_tokens=300, temperature=0.6, model="command")
        text = r.generations[0].text.strip()

    import json
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except Exception:
        return [{"title": text[:40], "duration": 45, "tag": "skill", "reason": "AI free-form response"}]
