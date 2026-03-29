"""
后端配置管理
支持多模型切换：Ollama（本地）/ OpenAI（云端）
"""
import os
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM 提供者：ollama | openai
    LLM_PROVIDER: Literal["ollama", "openai"] = "ollama"

    # OpenAI 配置（云端）
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # Ollama 配置（本地，推荐）
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # RAG 参数
    RETRIEVAL_TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.5
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # LLM 默认参数
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.9
    DEFAULT_MAX_TOKENS: int = 512

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
