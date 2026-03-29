"""
SiliconFlow Embedding 封装
绕过 tiktoken，直接发文本到 SiliconFlow API
解决 OpenAIEmbeddings + tiktoken 无法处理中文的问题
"""
import requests
from typing import List
from langchain_core.embeddings import Embeddings


class SiliconFlowEmbeddings(Embeddings):
    """SiliconFlow 中文优化 Embedding，BAAI/bge-large-zh-v1.5"""

    def __init__(self, api_key: str, model: str = "BAAI/bge-large-zh-v1.5"):
        self.api_key = api_key
        self.model = model
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量向量化文本"""
        embeddings = []
        # SiliconFlow 单次最多 25 条
        batch_size = 25
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            resp = self._session.post(
                "https://api.siliconflow.cn/v1/embeddings",
                json={"model": self.model, "input": batch},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            embeddings.extend([item["embedding"] for item in data["data"]])
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """单条查询向量化"""
        resp = self._session.post(
            "https://api.siliconflow.cn/v1/embeddings",
            json={"model": self.model, "input": text},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]
