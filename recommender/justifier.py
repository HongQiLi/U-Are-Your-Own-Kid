import os
import requests
from models.user_model import UserProfile
from recommender.core import build_prompt

# Function to generate reasoning using OpenAI GPT
def llm_openai(user_profile: UserProfile) -> str:
    prompt = build_prompt(user_profile)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "OpenAI API key not found."

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    return result.get("choices", [{}])[0].get("message", {}).get("content", "No response from OpenAI")

# Function to generate reasoning using Cohere
def llm_cohere(user_profile: UserProfile) -> str:
    prompt = build_prompt(user_profile)
    api_key = os.getenv("COHERE_API_KEY")

    if not api_key:
        return "Cohere API key not found."

    url = "https://api.cohere.ai/v1/chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "command-r",
        "message": prompt,
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    return result.get("text", "No response from Cohere")

# Function to generate reasoning using DeepSeek (hosted on Hugging Face)
def llm_deepseek(user_profile: UserProfile) -> str:
    prompt = build_prompt(user_profile)
    api_key = os.getenv("HF_API_KEY")

    if not api_key:
        return "Hugging Face API key not found."

    url = "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-coder-6.7b-instruct"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 150}
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    return result[0].get("generated_text", "No response from DeepSeek")
