# utils/cohere_client.py
# Cohere 客户端（推荐使用 chat 接口：command-r）
# Cohere client using the chat API (command-r)

import os
import cohere

def generate_cohere_reply(prompt: str) -> str:
    """
    生成 Cohere 回复（默认模型 command-r，可通过 COHERE_MODEL 覆盖）
    Generate a reply using Cohere (default model command-r; override via COHERE_MODEL).
    """
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        return "Cohere not configured: missing COHERE_API_KEY"

    try:
        # 惰性创建客户端，避免在模块导入时就因缺密钥崩溃
        # Lazy init to avoid crashing on import when no env is set
        co = cohere.Client(api_key)
        model = os.getenv("COHERE_MODEL", "command-r")

        # 新版推荐 chat 接口（5.x SDK）
        # Newer SDK prefers chat API
        resp = co.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        # 返回值中 message.content 可能是一个包含多个段落的列表
        # message.content may be a list of parts; join text fields
        parts = getattr(resp, "message", None)
        if parts and hasattr(parts, "content"):
            texts = []
            for part in parts.content:
                # SDK 里 part 可能是对象，也可能是字典；尽量兼容
                text = getattr(part, "text", None) or (part.get("text") if isinstance(part, dict) else None)
                if text:
                    texts.append(text)
            if texts:
                return "\n".join(texts).strip()

        # 回退到字符串化响应（不理想，但不至于报错）
        return str(resp)

    except Exception as e:
        return f"Cohere error: {str(e)}"
