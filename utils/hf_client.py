# utils/hf_client.py
# Hugging Face Inference API 客户端（可通过 HF_MODEL 指定模型）
# Hugging Face Inference API client (set model via HF_MODEL)

import os
import requests

def generate_reply(prompt: str) -> str:
    """
    使用 Hugging Face Inference API 生成文本。
    默认模型为 gpt2（很弱，建议你在 .env 里设 HF_MODEL=meta-llama/Meta-Llama-3-8B-Instruct 或 deepseek 模型）。
    Use HF Inference API; default model is gpt2 (weak). Prefer setting HF_MODEL in .env.
    """
    api_key = os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return "Hugging Face not configured: missing HF_API_KEY"

    model = os.getenv("HF_MODEL", "gpt2")
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 200}
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            return f"Hugging Face error: {r.status_code} {r.text}"

        data = r.json()

        # 常见返回格式：list[ { "generated_text": "..." } ]
        # Common format: a list with 'generated_text'
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            if isinstance(item, dict) and "generated_text" in item:
                return item["generated_text"]

        # 兼容其它可能格式
        if isinstance(data, dict):
            if "generated_text" in data:
                return data["generated_text"]
            if "error" in data:
                return f"Hugging Face error: {data['error']}"

        return "No response from Hugging Face."

    except Exception as e:
        return f"Hugging Face exception: {str(e)}"
