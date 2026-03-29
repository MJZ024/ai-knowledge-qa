"""
FastAPI 主入口
AI 智能知识库问答系统
学号：423830107 | 姓名：毛坚再
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api.routes import router

app = FastAPI(
    title="AI 智能知识库问答系统",
    description="基于 RAG 的智能问答系统，支持参数可视化调整",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "🤖 AI 智能知识库问答系统",
        "student_id": "423830107",
        "student_name": "毛坚再",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
