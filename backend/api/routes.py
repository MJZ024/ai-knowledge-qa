"""
API 路由
提供 RAG 问答、参数调整、知识库管理接口
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse

from ..core import settings, llm_manager, rag_retriever


router = APIRouter(prefix="/api", tags=["RAG 问答系统"])


# ============ 请求/响应模型 ============

class ChatRequest(BaseModel):
    query: str = Field(..., description="用户问题")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="创造性参数")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="核采样参数")
    max_tokens: int = Field(default=512, ge=64, le=4096, description="最大生成长度")
    system_prompt: str = Field(default="", description="自定义系统提示词")
    retrieval_top_k: int = Field(default=3, ge=1, le=10, description="检索文档数")
    similarity_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="相似度阈值")


class ChatResponse(BaseModel):
    answer: str
    retrieved_docs: List[str]
    params_used: dict
    model: str
    student_id: str = "423830107"
    student_name: str = "毛坚再"


class DocumentUploadRequest(BaseModel):
    texts: List[str] = Field(..., description="要添加的文档内容列表")
    metadata: Optional[dict] = Field(default=None, description="文档元数据")


class ParameterUpdateRequest(BaseModel):
    """参数更新请求（可部分更新）"""
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, ge=64, le=4096)
    retrieval_top_k: Optional[int] = Field(default=None, ge=1, le=10)
    similarity_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class ParameterResponse(BaseModel):
    """当前参数状态"""
    llm_provider: str
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    retrieval_top_k: int
    similarity_threshold: float


# ============ 路由定义 ============

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG 问答接口
    1. 检索知识库
    2. 构建提示词
    3. 调用 LLM 生成回答
    """
    # 更新检索参数
    rag_retriever.update_retrieval_params(
        request.retrieval_top_k, request.similarity_threshold
    )

    # 更新 LLM 参数
    llm_manager.update_params(
        request.temperature, request.top_p, request.max_tokens
    )

    # 检索相关文档
    retrieved_docs = rag_retriever.retrieve(
        request.query,
        top_k=request.retrieval_top_k,
        threshold=request.similarity_threshold,
    )

    # 构建提示词
    prompt = rag_retriever.build_prompt(
        request.query, retrieved_docs, request.system_prompt or None
    )

    # 调用 LLM
    answer = llm_manager.generate(prompt)

    return ChatResponse(
        answer=answer,
        retrieved_docs=[doc.page_content for doc in retrieved_docs],
        params_used={
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_tokens": request.max_tokens,
            "retrieval_top_k": request.retrieval_top_k,
            "similarity_threshold": request.similarity_threshold,
        },
        model=settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.OPENAI_MODEL,
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式问答接口"""
    rag_retriever.update_retrieval_params(
        request.retrieval_top_k, request.similarity_threshold
    )
    llm_manager.update_params(
        request.temperature, request.top_p, request.max_tokens
    )

    retrieved_docs = rag_retriever.retrieve(
        request.query, request.retrieval_top_k, request.similarity_threshold
    )
    prompt = rag_retriever.build_prompt(
        request.query, retrieved_docs, request.system_prompt or None
    )

    return StreamingResponse(
        llm_manager.stream_generate(prompt),
        media_type="text/plain; charset=utf-8",
    )


@router.get("/params", response_model=ParameterResponse)
async def get_params():
    """获取当前参数状态"""
    current_params = llm_manager.get_current_params()
    return ParameterResponse(
        llm_provider=settings.LLM_PROVIDER,
        model=current_params.get("model", ""),
        temperature=current_params.get("temperature", settings.DEFAULT_TEMPERATURE),
        top_p=current_params.get("top_p", settings.DEFAULT_TOP_P),
        max_tokens=current_params.get("max_tokens", settings.DEFAULT_MAX_TOKENS),
        retrieval_top_k=settings.RETRIEVAL_TOP_K,
        similarity_threshold=settings.SIMILARITY_THRESHOLD,
    )


@router.post("/params", response_model=ParameterResponse)
async def update_params(request: ParameterUpdateRequest):
    """更新参数（运行时调整，无需重启）"""
    current_params = llm_manager.get_current_params()

    temperature = request.temperature if request.temperature is not None else current_params.get("temperature", 0.7)
    top_p = request.top_p if request.top_p is not None else current_params.get("top_p", 0.9)
    max_tokens = request.max_tokens if request.max_tokens is not None else current_params.get("max_tokens", 512)

    llm_manager.update_params(temperature, top_p, max_tokens)

    if request.retrieval_top_k is not None:
        settings.RETRIEVAL_TOP_K = request.retrieval_top_k
    if request.similarity_threshold is not None:
        settings.SIMILARITY_THRESHOLD = request.similarity_threshold

    return ParameterResponse(
        llm_provider=settings.LLM_PROVIDER,
        model=current_params.get("model", ""),
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        retrieval_top_k=settings.RETRIEVAL_TOP_K,
        similarity_threshold=settings.SIMILARITY_THRESHOLD,
    )


@router.post("/knowledge/add")
async def add_documents(request: DocumentUploadRequest):
    """向知识库添加文档"""
    try:
        count = rag_retriever.add_documents(
            request.texts, [request.metadata] * len(request.texts)
        )
        return {"status": "success", "chunks_added": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/reset")
async def reset_knowledge_base():
    """重置知识库"""
    rag_retriever.reset_knowledge_base()
    return {"status": "success", "message": "知识库已重置"}


@router.get("/status")
async def get_status():
    """系统状态检查"""
    return {
        "status": "running",
        "llm_provider": settings.LLM_PROVIDER,
        "model": settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.OPENAI_MODEL,
        "student_id": "423830107",
        "student_name": "毛坚再",
    }
