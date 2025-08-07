# utils/openai_client.py
# 用于调用 OpenAI GPT 模型的函数

import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_openai_reply(prompt: str) -> str:
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()
