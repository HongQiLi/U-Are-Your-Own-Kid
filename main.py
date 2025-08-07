# main.py
# 应用主入口 / Application Entry Point

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from routers import user, schedule, recommender, feedback, parent, calendar_sync
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from utils.interest_extractor import extract_interest_from_survey
from utils.hf_client import generate_reply as hf_reply
from utils.cohere_client import generate_cohere_reply as cohere_reply
from utils.openai_client import generate_openai_reply as openai_reply

# 创建 FastAPI 实例 / Create FastAPI app
app = FastAPI(
    title="U-Are-Your-Own-Kid",
    description="An intelligent platform for personalized growth planning",
    version="1.0.0"
)

# 首页路由
@app.get("/")
def serve_home():
    return FileResponse("front/index.html")

# 日历页面路由
@app.get("/calendar-page")
def serve_calendar():
    return FileResponse("front/calendar.html")

# 兴趣提取接口
@app.post("/test-interest")
async def test_interest_extraction(data: dict):
    return {
        "interests": extract_interest_from_survey(data)
    }

# 测试 LLM 输出
@app.get("/test-llm")
async def test_llm(request: Request):
    prompt = "Give me 3 creative ways to help kids build self-discipline."

    try:
        hf_output = hf_reply(prompt)
    except Exception as e:
        hf_output = f"HuggingFace error: {str(e)}"

    try:
        cohere_output = cohere_reply(prompt)
    except Exception as e:
        cohere_output = f"Cohere error: {str(e)}"

    try:
        openai_output = openai_reply(prompt)
    except Exception as e:
        openai_output = f"OpenAI error: {str(e)}"

    return {
        "huggingface": hf_output,
        "cohere": cohere_output,
        "openai": openai_output
    }

# 注册各功能模块对应的路由 / Register routers for each module
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
app.include_router(recommender.router, prefix="/recommend", tags=["Recommender"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(parent.router, prefix="/parent", tags=["Parent"])
app.include_router(calendar_sync.router, prefix="/calendar", tags=["Calendar"])

# 静态文件挂载 / Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 运行方法 / Run the app:
# uvicorn main:app --reload
