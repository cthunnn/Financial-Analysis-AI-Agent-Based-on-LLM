"""
backend/app/core/llm.py
LLM 大模型统一调用接口 - 支持 OpenAI 兼容协议的多种模型供应商
"""
import time
import logging
from typing import Optional, AsyncIterator, Any, Dict, List
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class LLMCallLog:
    """LLM 单次调用日志记录"""
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost_usd: float
    timestamp: str
    success: bool
    error: Optional[str] = None


class TokenCostCalculator:
    """
    Token 成本计算器
    根据模型名称自动匹配对应的价格策略
    注：价格为示例值，实际价格请参考各模型供应商官方定价
    """

    # 每千 Token 价格（美元）
    GPT4O_INPUT = 0.0025 / 1000
    GPT4O_OUTPUT = 0.01 / 1000
    QWEN_INPUT = 0.001 / 1000
    QWEN_OUTPUT = 0.002 / 1000
    DEEPSEEK_INPUT = 0.001 / 1000
    DEEPSEEK_OUTPUT = 0.002 / 1000

    @classmethod
    def calculate(cls, model: str, input_tokens: int, output_tokens: int) -> float:
        """根据模型名称和 Token 数量计算本次调用的预估成本"""
        model_lower = model.lower()
        if "gpt-4o" in model_lower or "gpt-4" in model_lower:
            return input_tokens * cls.GPT4O_INPUT + output_tokens * cls.GPT4O_OUTPUT
        elif "qwen" in model_lower:
            return input_tokens * cls.QWEN_INPUT + output_tokens * cls.QWEN_OUTPUT
        elif "deepseek" in model_lower:
            return input_tokens * cls.DEEPSEEK_INPUT + output_tokens * cls.DEEPSEEK_OUTPUT
        return 0.0


class LLMService:
    """
    LLM 大模型统一服务接口
    封装 ChatOpenAI 和 OpenAIEmbeddings，提供对话、流式输出、文本向量化三种能力
    支持所有兼容 OpenAI API 协议的模型供应商（通义千问、DeepSeek、GPT-4 等）
    """

    def __init__(self):
        self.settings = get_settings()
        self._llm: Optional[ChatOpenAI] = None
        self._embeddings: Optional[OpenAIEmbeddings] = None

    @property
    def llm(self) -> ChatOpenAI:
        """延迟初始化 LLM 对话客户端"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.settings.LLM_MODEL,
                api_key=self.settings.LLM_API_KEY,
                base_url=self.settings.LLM_API_BASE,
                temperature=self.settings.LLM_TEMPERATURE,
                max_tokens=self.settings.LLM_MAX_TOKENS,
                timeout=self.settings.LLM_TIMEOUT,
                streaming=True,
            )
            logger.info(f"[LLM] 初始化完成: model={self.settings.LLM_MODEL}")
        return self._llm

    @property
    def embeddings(self) -> OpenAIEmbeddings:
        """延迟初始化 Embedding 客户端"""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                model=self.settings.EMBEDDING_MODEL,
                api_key=self.settings.EMBEDDING_API_KEY or self.settings.LLM_API_KEY,
                base_url=self.settings.EMBEDDING_API_BASE or self.settings.LLM_API_BASE,
            )
            logger.info(f"[Embedding] 初始化完成: model={self.settings.EMBEDDING_MODEL}")
        return self._embeddings

    async def chat(
        self,
        messages: List[BaseMessage],
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
        stream: bool = False,
    ) -> tuple[str, LLMCallLog]:
        """
        通用对话接口

        Args:
            messages: 对话消息列表
            tools: 可选的 Function Calling 工具定义
            tool_choice: 工具选择策略
            stream: 是否启用流式输出

        Returns:
            (响应文本, 调用日志)
        """
        start_time = time.time()

        try:
            if tools:
                llm_with_tools = self.llm.bind_tools(tools)
                response = await llm_with_tools.ainvoke(messages)
            else:
                response = await self.llm.ainvoke(messages)

            latency = (time.time() - start_time) * 1000
            content = response.content if hasattr(response, "content") else str(response)

            # 提取 Token 用量
            usage = getattr(response, "response_metadata", {}).get("token_usage", {})
            if usage:
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
            else:
                # 降级估算
                prompt_tokens = sum(len(str(m.content or "")) for m in messages) // 4
                completion_tokens = len(content) // 4

            total_tokens = prompt_tokens + completion_tokens
            cost = TokenCostCalculator.calculate(
                self.settings.LLM_MODEL, prompt_tokens, completion_tokens
            )

            log = LLMCallLog(
                model=self.settings.LLM_MODEL,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency,
                cost_usd=cost,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                success=True,
            )

            logger.info(
                f"[LLM] model={self.settings.LLM_MODEL} "
                f"tokens={total_tokens} latency={latency:.0f}ms cost=${cost:.6f}"
            )
            return content, log

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"[LLM] 调用失败: {str(e)}")
            log = LLMCallLog(
                model=self.settings.LLM_MODEL,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency_ms=latency,
                cost_usd=0.0,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error=str(e),
            )
            return "", log

    async def chat_stream(
        self, messages: List[BaseMessage]
    ) -> AsyncIterator[tuple[str, Optional[LLMCallLog]]]:
        """
        流式对话接口

        Args:
            messages: 对话消息列表

        Yields:
            (token片段, 结束时的调用日志或None)
        """
        start_time = time.time()
        full_response = ""

        try:
            async for chunk in self.llm.astream(messages):
                token = chunk.content if hasattr(chunk, "content") else str(chunk)
                if token:
                    full_response += token
                    yield token, None

            latency = (time.time() - start_time) * 1000
            prompt_tokens = sum(len(str(m.content or "")) for m in messages) // 4
            completion_tokens = len(full_response) // 4
            total_tokens = prompt_tokens + completion_tokens
            cost = TokenCostCalculator.calculate(
                self.settings.LLM_MODEL, prompt_tokens, completion_tokens
            )

            log = LLMCallLog(
                model=self.settings.LLM_MODEL,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency,
                cost_usd=cost,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                success=True,
            )
            yield "", log

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"[LLM] 流式调用失败: {str(e)}")
            log = LLMCallLog(
                model=self.settings.LLM_MODEL,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency_ms=latency,
                cost_usd=0.0,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error=str(e),
            )
            yield "", log

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        文本向量化接口

        Args:
            texts: 待向量化的文本列表

        Returns:
            向量列表，每个向量为 float 列表
        """
        try:
            embeddings = await self.embeddings.aembed_documents(texts)
            logger.info(f"[Embedding] 已处理 {len(texts)} 条文本, 维度={len(embeddings[0]) if embeddings else 0}")
            return embeddings
        except Exception as e:
            logger.error(f"[Embedding] 向量化失败: {str(e)}")
            raise


# 模块级单例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取 LLMService 单例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
