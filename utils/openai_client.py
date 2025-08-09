# utils/openai_client.py
# OpenAI 客户端（Chat Completions，新版 SDK）
# OpenAI client using the modern Chat Completions API

import os
from openai import OpenAI

def _get_openai_client():
    """
    懒加载 OpenAI 客户端；如果没有配置密钥，不抛异常，交给上层处理。
    Lazy-create OpenAI client; do not crash import if key is missing.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def generate_openai_reply(prompt: str) -> str:
    """
    生成 OpenAI 回复（默认 gpt-4o-mini，可通过环境变量 OPENAI_MODEL 覆盖）
    Generate a reply using OpenAI (default gpt-4o-mini; override via OPENAI_MODEL).
    """
    client = _get_openai_client()
    if client is None:
        return "OpenAI not configured: missing OPENAI_API_KEY"

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful planner for youth growth and study."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        content = resp.choices[0].message.content if resp.choices else ""
        return content.strip() if content else "No content from OpenAI."
    except Exception as e:
        return f"OpenAI error: {str(e)}"
