# utils/hf_client.py
# Hugging Face Inference API。请选择一个可用的公开模型（这里用 mistralai/Mistral-7B-Instruct-v0.2）

import os, json, requests
from typing import List

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

def generate_reply(prompt: str) -> str:
    if not HEADERS["Authorization"].endswith(("None", "", " ")):
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 200, "temperature": 0.7}}
        r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        if r.status_code == 200:
            out = r.json()
            # 兼容多种返回结构
            if isinstance(out, list) and len(out) and "generated_text" in out[0]:
                return out[0]["generated_text"]
            if isinstance(out, dict) and "generated_text" in out:
                return out["generated_text"]
            return str(out)[:500]
        return f"Hugging Face error: {r.status_code} {r.text}"
    return "Hugging Face not configured: missing HUGGINGFACE_API_KEY"

def suggest_activities_with_hf(prompt: str) -> List[dict]:
    sys = (
        "Return 3-5 kid-friendly activity suggestions as a JSON array. "
        "Each item: {\"title\": str, \"duration\": int minutes, \"tag\": \"skill|reading|sport|social|art\", \"reason\": str}."
    )
    text = generate_reply(sys + "\nUser: " + prompt)
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except Exception:
        return [{"title": text[:40], "duration": 45, "tag": "skill", "reason": "AI free-form response"}]
