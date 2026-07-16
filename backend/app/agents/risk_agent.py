"""
backend/app/agents/risk_agent.py
风控预警 Agent - 负责风险识别、量化评估与预警监控
"""
from typing import Dict, Any

from langchain.tools import tool

from app.agents.base import BaseAgent, AgentConfig, AgentExecutionResult
from app.models.schemas import AgentType


# ===== 工具定义（需对接实际数据源后替换为实现） =====

@tool(description="计算股票风险指标：波动率、VaR、Beta等")
def calculate_risk_metrics(stock_code: str, period: int = 60) -> str:
    # TODO: 对接实际风控计算引擎
    return f'{{"code": "{stock_code}", "volatility": 0.25, "var_95": -0.03, "beta": 1.2}}'


@tool(description="查询监管处罚和诉讼信息")
def check_regulatory_events(stock_code: str) -> str:
    # TODO: 对接监管信息API
    return f'[{{"event": "处罚/诉讼事件(待对接)", "date": "日期", "severity": "中等"}}]'


# ===== Agent 提示词 =====

RISK_AGENT_SYSTEM_PROMPT = """你是一位专业金融风控专家，擅长风险量化分析、预警模型构建与合规审查。

风控评估维度：
- 财务风险：盈利质量分析、现金流异常检测、债务结构评估
- 经营风险：大客户依赖度、竞争壁垒评估、管理层稳定性
- 市场风险：波动率分析、VaR在险价值、Beta系统性风险系数
- 合规风险：监管处罚记录、信息披露违规、诉讼风险

风险等级划分（0-100分制）：
- 红色 高风险（80-100分）：存在重大风险隐患，建议高度警惕
- 橙色 中高风险（60-79分）：风险因素较多，建议持续关注
- 黄色 中风险（40-59分）：存在常规风险，建议定期复查
- 绿色 低风险（0-39分）：风险可控，无明显异常

输出要求：
- 逐项列出风险因子及对应的风险等级
- 给出综合风险评分与等级
- 关键风险使用 [风险] 前缀标注
- 提供风险应对建议"""


class RiskAgent(BaseAgent):
    """风控Agent：负责风险评估、量化分析与预警"""

    def __init__(self):
        tools = [calculate_risk_metrics, check_regulatory_events]
        config = AgentConfig(
            name="风控预警Agent",
            agent_type=AgentType.RISK,
            description="风险识别、量化评估、预警监控",
            system_prompt=RISK_AGENT_SYSTEM_PROMPT,
            tools=tools,
            max_iterations=6,
        )
        super().__init__(config)

    def _build_system_prompt(self) -> str:
        return self.config.system_prompt

    def _parse_output(self, raw_output: str) -> Dict[str, Any]:
        return {"analysis": raw_output, "agent_type": "risk"}

    async def assess_risk(self, stock_code: str, query: str = "") -> AgentExecutionResult:
        """便捷方法：快速评估某只股票的风险"""
        task = (
            f"对股票 {stock_code} 进行全面风险评估。"
            f"请计算核心风险指标，检查监管处罚事件，识别主要财务风险与经营风险，"
            f"输出综合风险评分（0-100分）及对应的风险等级。"
            f"{query}"
        )
        return await self.execute(task=task)
