# routers/llm_reason.py
# Explainable AI reasoning via different LLMs (OpenAI, Cohere, DeepSeek)

from fastapi import APIRouter, HTTPException, Query
from models.user_profile import UserProfile
from recommender.justifier import llm_openai, llm_cohere, llm_deepseek

router = APIRouter()

@router.post("/recommend/llm_reason")
def get_llm_reason(user_profile: UserProfile, provider: str = Query("openai")):
    """
    Generate human-style explanation for recommended tasks using selected LLM.

    Parameters:
    - user_profile (UserProfile): user information, including survey and availability
    - provider (str): LLM provider, choose from: openai / cohere / deepseek

    Returns:
    - reason (str): natural language explanation of why these tasks are suitable
    """
    try:
        if provider == "openai":
            return {"reason": llm_openai(user_profile)}
        elif provider == "cohere":
            return {"reason": llm_cohere(user_profile)}
        elif provider == "deepseek":
            return {"reason": llm_deepseek(user_profile)}
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM reasoning failed: {str(e)}")
