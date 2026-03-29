"""
RAG 检索器
基于 ChromaDB 向量数据库 + 可切换 Embedding 模型
支持：ollama（本地）/ siliconflow（国内 AI）
"""
import os
from typing import List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from .embeddings import SiliconFlowEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .config import settings


class RAGRetriever:
    """RAG 检索器，管理知识库和向量检索"""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.embedding_model = self._init_embedding()
        self.vectorstore: Optional[Chroma] = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        self._init_vectorstore()

    def _init_embedding(self):
        """根据 LLM 提供者选择对应的 Embedding 模型"""
        if settings.LLM_PROVIDER == "siliconflow":
            return SiliconFlowEmbeddings(
                api_key=settings.SILICONFLOW_API_KEY,
                model=settings.SILICONFLOW_EMBEDDING_MODEL,
            )
        else:
            return OllamaEmbeddings(
                model=settings.OLLAMA_EMBEDDING_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
            )

    def _init_vectorstore(self):
        """初始化向量数据库（加载已有或新建空库）"""
        try:
            self.vectorstore = Chroma(
                client=self.client,
                embedding_function=self.embedding_model,
                collection_name="knowledge_base",
            )
        except Exception:
            self.vectorstore = Chroma(
                client=self.client,
                embedding_function=self.embedding_model,
                collection_name="knowledge_base",
                persist_directory=settings.CHROMA_PERSIST_DIR,
            )

    def add_documents(self, texts: List[str], metadatas: List[dict] = None):
        """向知识库添加文档"""
        if metadatas is None:
            metas: List[dict] = [{}] * len(texts)
        else:
            metas = [m or {} for m in metadatas]
        docs = [Document(page_content=t, metadata=m) for t, m in zip(texts, metas)]
        chunks = self.text_splitter.split_documents(docs)

        if self.vectorstore is None:
            self._init_vectorstore()

        self.vectorstore.add_documents(chunks)
        return len(chunks)

    def update_retrieval_params(self, top_k: int, threshold: float):
        """更新检索参数"""
        settings.RETRIEVAL_TOP_K = top_k
        settings.SIMILARITY_THRESHOLD = threshold

    def retrieve(self, query: str, top_k: int = None, threshold: float = None) -> List[Document]:
        """检索相关文档"""
        if self.vectorstore is None:
            return []

        top_k = top_k or settings.RETRIEVAL_TOP_K
        threshold = threshold or settings.SIMILARITY_THRESHOLD

        results = self.vectorstore.similarity_search_with_score(
            query, k=top_k
        )
        # 过滤低于阈值的文档
        filtered = [doc for doc, score in results if score >= threshold]
        return filtered

    def build_prompt(self, query: str, retrieved_docs: List[Document], system_prompt: str = None) -> str:
        """构建 RAG 提示词"""
        if not retrieved_docs:
            return query

        context = "\n\n".join([f"[文档 {i+1}]\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)])

        system = system_prompt or (
            "你是一个智能助手。请根据以下参考文档回答用户问题。"
            "如果文档中没有相关信息，请如实说明。"
        )

        prompt = f"{system}\n\n## 参考文档：\n{context}\n\n## 用户问题：\n{query}\n\n## 回答："
        return prompt

    def reset_knowledge_base(self):
        """重置知识库"""
        try:
            self.client.delete_collection("knowledge_base")
            self.vectorstore = None
            self._init_vectorstore()
        except Exception:
            pass


rag_retriever = RAGRetriever()
