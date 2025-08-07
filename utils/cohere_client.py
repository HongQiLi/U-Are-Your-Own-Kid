# utils/cohere_client.py
# 用于调用 Cohere 模型的函数

import cohere
import os

co = cohere.Client(os.getenv('COHERE_API_KEY'))

def generate_cohere_reply(prompt: str) -> str:
    response = co.generate(prompt=prompt, max_tokens=100)
    return response.generations[0].text.strip()
