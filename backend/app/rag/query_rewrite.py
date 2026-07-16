"""
backend/app/rag/query_rewrite.py
查询改写模块 - 通过 LLM 优化用户查询，提升检索召回率
"""
import re
import json
import logging
from typing import Dict, Any

from langchain.schema import HumanMessage

from app.core.llm import get_llm_service

logger = logging.getLogger(__name__)


class QueryRewriter:
    """
    查询改写器
    功能：术语标准化 | 意图识别 | 同义词扩展 | 股票代码补全
    """

    REWRITE_PROMPT = """你是一位专业的金融搜索引擎查询优化助手。

原始查询：{original_query}

请对查询进行优化处理：
1. 术语标准化：将口语化表达转为标准金融术语（如"茅台" -> "贵州茅台(600519)"）
2. 意图识别：判断查询属于以下哪种类型——投研分析 / 风险评估 / 策略建议 / 知识问答
3. 查询扩展：如有必要，补充同义词和相关术语

请严格按以下JSON格式输出，不要包含其他内容：
{{"rewritten_query": "优化后的查询文本", "intent": "意图类型", "stock_codes": ["股票代码"], "stock_names": ["股票名称"], "notes": "补充说明"}}"""

    def __init__(self):
        self.llm = get_llm_service()

    async def rewrite(self, query: str) -> Dict[str, Any]:
        """对用户查询进行改写优化"""
        try:
            messages = [
                HumanMessage(content=self.REWRITE_PROMPT.format(original_query=query))
            ]
            content, log = await self.llm.chat(messages, stream=False)

            if not log.success or not content:
                return self._fallback(query)

            # 提取JSON
            json_match = re.search(
                r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL
            )
            if json_match:
                result = json.loads(json_match.group(0))
                return result

            return self._fallback(query)

        except Exception as e:
            logger.warning(f"[查询改写] 失败: {str(e)}")
            return self._fallback(query)

    def _fallback(self, query: str) -> Dict[str, Any]:
        """改写失败时的降级策略"""
        return {
            "rewritten_query": query,
            "intent": "unknown",
            "stock_codes": [],
            "stock_names": [],
            "expand_queries": [],
        }
