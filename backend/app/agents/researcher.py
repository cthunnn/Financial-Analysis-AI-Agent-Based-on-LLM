"""
backend/app/agents/researcher.py
投研分析 Agent - 负责股票基本面分析、财务解读与估值研判
"""
from typing import Dict, Any

from langchain.tools import tool

from app.agents.base import BaseAgent, AgentConfig, AgentExecutionResult
from app.models.schemas import AgentType


# ===== 工具定义（需对接实际数据源后替换为实现） =====

@tool(description="查询股票基本信息：代码、名称、行业、上市日期、市值等")
def get_stock_info(stock_code: str) -> str:
    # TODO: 对接实际数据源（Wind / Tushare / 东方财富API）
    return f'{{"code": "{stock_code}", "name": "股票名称(待对接)", "industry": "行业分类(待对接)"}}'


@tool(description="查询股票财务数据：营收、净利润、毛利率、ROE等")
def get_stock_financials(stock_code: str, period: str = "annual") -> str:
    # TODO: 对接实际数据源
    return f'{{"code": "{stock_code}", "period": "{period}", "revenue": 0, "net_profit": 0, "roe": 0.0}}'


@tool(description="查询股票K线数据（开盘价、最高价、最低价、收盘价、成交量）")
def get_stock_kline(stock_code: str, days: int = 60) -> str:
    # TODO: 对接实际数据源
    return f'[{{"date": "2024-01-01", "open": 0, "high": 0, "low": 0, "close": 0, "volume": 0}}]'


@tool(description="搜索财经新闻和公告")
def search_financial_news(keyword: str, limit: int = 10) -> str:
    # TODO: 对接新闻API
    return f'[{{"title": "新闻标题(待对接)", "source": "来源(待对接)", "date": "2024-01-01"}}]'


# ===== Agent 提示词 =====

RESEARCHER_SYSTEM_PROMPT = """你是一位资深金融投研分析师，拥有10年以上经验，擅长基本面分析与财务建模。

分析框架：
- 业绩驱动因素：识别营收增长的核心来源，评估市场份额变化趋势
- 盈利能力分析：分析毛利率、净利率、ROE的变动趋势及其驱动因素
- 估值判断：从横向（与同行业对比）和纵向（与历史区间对比）两个维度评估当前估值水平
- 风险提示：识别经营风险、财务风险、行业周期风险
- 投资建议：基于以上分析给出客观结论

输出要求：
- 使用 Markdown 结构化格式
- 数据需标明来源
- 关键结论使用**加粗**标注
- 风险因素以 [风险] 前缀标注"""


class ResearcherAgent(BaseAgent):
    """投研分析Agent：负责股票研究、财务分析和估值"""

    def __init__(self):
        tools = [get_stock_info, get_stock_financials, get_stock_kline, search_financial_news]
        config = AgentConfig(
            name="投研分析Agent",
            agent_type=AgentType.RESEARCHER,
            description="股票基本面分析、财务解读、估值研判",
            system_prompt=RESEARCHER_SYSTEM_PROMPT,
            tools=tools,
            max_iterations=8,
        )
        super().__init__(config)

    def _build_system_prompt(self) -> str:
        return self.config.system_prompt

    def _parse_output(self, raw_output: str) -> Dict[str, Any]:
        return {"analysis": raw_output, "agent_type": "researcher"}

    async def analyze_stock(self, stock_code: str, query: str = "") -> AgentExecutionResult:
        """便捷方法：快速分析某只股票"""
        task = (
            f"对股票 {stock_code} 进行全面分析。"
            f"请获取基本信息、最近财务数据，进行估值分析，对比同行业情况，输出综合研判。"
            f"{query}"
        )
        return await self.execute(task=task)
