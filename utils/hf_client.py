# utils/hf_client.py
# 用于调用 Huggingface 模型的函数

import requests
import os

API_URL = "https://api-inference.huggingface.co/models/gpt2"
HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

def generate_reply(prompt: str) -> str:
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        generated = response.json()
        return generated[0]["generated_text"]
    else:
        raise Exception(f"Huggingface API Error: {response.text}")
