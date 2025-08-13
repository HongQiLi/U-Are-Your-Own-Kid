# recommender/justifier.py
# Module: Task Explanation Generator using Rule-Based and LLM Approaches
# Description: Provides both rule-based and LLM-based reasoning for task recommendations

import os
import requests
from models.user_profile import UserProfile
from models.task_model import Task
from recommender.core import build_prompt  # Prompt construction logic for LLM

# Function: Generate rule-based explanation without LLM
def generate_rule_based_reason(task):
    """
    Generate a simple explanation based on task tags.
    This is used when LLM is not available or not preferred.
    """
    return f"The task '{task.name}' is recommended based on your interests: {task.tags}."

# Function: Use OpenAI GPT to generate explanation
def llm_openai(user_profile):
    """
    Generate explanation using OpenAI GPT (gpt-3.5-turbo).
    Requires OPENAI_API_KEY in environment variables.
    """
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

# Function: Use Cohere API to generate explanation
def llm_cohere(user_profile):
    """
    Generate explanation using Cohere API (command-r model).
    Requires COHERE_API_KEY in environment variables.
    """
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

# Function: Use DeepSeek via Hugging Face API to generate explanation
def llm_deepseek(user_profile):
    """
    Generate explanation using DeepSeek (hosted on Hugging Face).
    Requires HF_API_KEY (Hugging Face Token) in environment variables.
    """
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
        "parameters": {
            "max_new_tokens": 150
        }
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "No response from DeepSeek")
    else:
        return "Invalid response format from DeepSeek"
