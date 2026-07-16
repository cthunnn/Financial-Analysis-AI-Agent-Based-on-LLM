"""
backend/app/api/chat.py
对话 API - 智能投研对话的核心接口，集成 RAG 检索与 Agent 编排
"""
import uuid
import time
import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse, AgentType
from app.agents.orchestrator import get_orchestrator
from app.llmops.monitor import get_llmops_monitor
from app.rag.retriever import get_hybrid_retriever
from app.core.llm import get_llm_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    智能对话接口

    流程：接收用户消息 -> RAG知识检索 -> Agent编排执行 -> 返回分析结果
    支持多Agent协同分析，自动进行意图分类与任务调度
    """
    session_id = request.session_id or str(uuid.uuid4())
    start_time = time.time()
    context = {}

    try:
        # Step 1: RAG 知识检索
        sources = []
        if request.enable_rag:
            retriever = get_hybrid_retriever()
            chunks = await retriever.retrieve(
                query=request.message,
                top_k=5,
                enable_rerank=True,
            )
            if chunks:
                context["rag_context"] = chunks
                sources = [{
                    "content": c["content"][:200] + "...",
                    "score": round(c["score"], 3),
                    "metadata": c.get("metadata", {}),
                } for c in chunks]

        # Step 2: Agent 编排执行
        orchestrator = get_orchestrator()
        agent_types = [request.agent_type] if request.agent_type else None

        result = await orchestrator.run(
            query=request.message,
            session_id=session_id,
            agent_types=agent_types,
            parallel=False,  # 对话场景使用串行以保证上下文连贯
            context=context,
        )

        latency = (time.time() - start_time) * 1000

        # Step 3: 记录 LLMOps 调用日志
        monitor = get_llmops_monitor()
        monitor.log_call(
            model="orchestrator",
            prompt_tokens=len(request.message) // 4,
            completion_tokens=len(result["final_response"]) // 4,
            total_tokens=result["execution_summary"]["total_tokens"],
            latency_ms=latency,
            cost_usd=0.0,
            success=True,
            session_id=session_id,
            prompt_preview=request.message[:100],
        )

        return ChatResponse(
            session_id=session_id,
            message=result["final_response"],
            agent_type=AgentType.RESEARCHER,
            sources=sources if sources else None,
            token_usage={"total": result["execution_summary"]["total_tokens"]},
            latency_ms=round(latency, 2),
        )

    except Exception as e:
        logger.error(f"[对话API] 处理失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式对话接口 (Server-Sent Events)

    使用 SSE 协议逐步推送Agent分析结果，
    提供更快的首字响应体验
    """
    session_id = request.session_id or str(uuid.uuid4())

    async def event_generator() -> AsyncIterator[str]:
        try:
            # RAG 检索
            context = {}
            if request.enable_rag:
                retriever = get_hybrid_retriever()
                chunks = await retriever.retrieve(
                    query=request.message, top_k=5, enable_rerank=True,
                )
                if chunks:
                    context["rag_context"] = chunks

            # Agent 流式执行
            orchestrator = get_orchestrator()
            result = await orchestrator.run(
                query=request.message,
                session_id=session_id,
                context=context,
            )

            response_text = result["final_response"]

            # 将完整响应分块发送以模拟流式效果
            # TODO: 接入 Agent 真正的流式输出能力
            chunk_size = 80
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i + chunk_size]
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            # 发送完成信号与元数据
            yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'tokens': result['execution_summary']['total_tokens']})}\n\n"

        except Exception as e:
            logger.error(f"[流式对话] 异常: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
