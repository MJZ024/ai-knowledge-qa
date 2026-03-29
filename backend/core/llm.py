"""
LLM 调用封装
支持 Ollama（本地）、OpenAI（云端）、SiliconFlow（国内 AI）
"""
import os
from typing import Generator, Optional
from langchain_community.llms import Ollama
from langchain_openai import OpenAI

from .config import settings


class LLMManager:
    """LLM 管理器，支持参数动态调整"""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self._llm: Optional[OpenAI | Ollama] = None
        self._init_llm()

    def _init_llm(self):
        if self.provider == "openai":
            self._llm = OpenAI(
                api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", ""),
                model=settings.OPENAI_MODEL,
                temperature=settings.DEFAULT_TEMPERATURE,
                max_tokens=settings.DEFAULT_MAX_TOKENS,
            )
        elif self.provider == "siliconflow":
            # SiliconFlow 兼容 OpenAI 接口，只需改 base_url 和 api_key
            self._llm = OpenAI(
                api_key=settings.SILICONFLOW_API_KEY,
                model=settings.SILICONFLOW_MODEL,
                base_url="https://api.siliconflow.cn/v1",
                temperature=settings.DEFAULT_TEMPERATURE,
                max_tokens=settings.DEFAULT_MAX_TOKENS,
            )
        else:  # ollama (default)
            self._llm = Ollama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                temperature=settings.DEFAULT_TEMPERATURE,
                options={
                    "num_ctx": 4096,
                    "top_p": settings.DEFAULT_TOP_P,
                },
            )

    def update_params(self, temperature: float, top_p: float, max_tokens: int):
        """运行时更新 LLM 参数"""
        if self.provider in ("openai", "siliconflow"):
            self._llm.temperature = temperature
            self._llm.max_tokens = max_tokens
        else:
            self._llm.temperature = temperature
            self._llm.options["top_p"] = top_p
            self._llm.options["num_predict"] = max_tokens

    def generate(self, prompt: str) -> str:
        """同步生成"""
        return self._llm.invoke(prompt)

    def stream_generate(self, prompt: str) -> Generator[str, None, None]:
        """流式生成"""
        for chunk in self._llm.stream(prompt):
            yield chunk

    def get_current_params(self) -> dict:
        """获取当前 LLM 参数"""
        if self.provider in ("openai", "siliconflow"):
            return {
                "provider": self.provider,
                "model": self._llm.model if self.provider == "siliconflow" else settings.OPENAI_MODEL,
                "temperature": self._llm.temperature,
                "max_tokens": self._llm.max_tokens,
            }
        else:
            return {
                "provider": "ollama",
                "model": settings.OLLAMA_MODEL,
                "temperature": self._llm.temperature,
                "top_p": self._llm.options.get("top_p", 0.9),
                "max_tokens": self._llm.options.get("num_predict", 512),
            }


llm_manager = LLMManager()
