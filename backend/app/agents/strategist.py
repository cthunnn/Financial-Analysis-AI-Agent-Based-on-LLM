"""
backend/app/agents/strategist.py
策略生成 Agent - 负责投资策略制定、组合建议与交易方案设计
"""
from typing import Dict, Any

from app.agents.base import BaseAgent, AgentConfig, AgentExecutionResult
from app.models.schemas import AgentType


# ===== Agent 提示词 =====

STRATEGIST_SYSTEM_PROMPT = """你是一位资深量化投资策略师，精通多因子模型构建与资产配置优化。

策略设计原则：
- 风险收益匹配：根据用户风险偏好设计对应策略，诚实告知预期收益与最大回撤
- 分散化投资：单一标的仓位建议不超过总仓位的20%，行业集中度不超过40%
- 流动性优先：优先选择日均成交额超过1亿元的标的
- 动态调整：根据市场环境变化调整仓位和止损线

策略输出框架：
1. 策略概述：策略类型、适用市场环境、预期年化收益与最大回撤
2. 选股标准：行业偏好、市值范围、估值筛选条件、技术指标要求
3. 仓位配置：各标的建议仓位比例、入场价格区间、止损价位
4. 风险控制：最大回撤控制线、动态止损规则、极端行情应对预案

重要声明：以下内容仅供参考学习，不构成任何形式的投资建议。投资有风险，入市需谨慎。"""


class StrategistAgent(BaseAgent):
    """策略Agent：负责投资策略建议与组合配置"""

    def __init__(self):
        config = AgentConfig(
            name="策略生成Agent",
            agent_type=AgentType.STRATEGIST,
            description="投资策略制定、组合建议、交易方案设计",
            system_prompt=STRATEGIST_SYSTEM_PROMPT,
            tools=[],
            max_iterations=5,
        )
        super().__init__(config)

    def _build_system_prompt(self) -> str:
        return self.config.system_prompt

    def _parse_output(self, raw_output: str) -> Dict[str, Any]:
        return {"strategy": raw_output, "agent_type": "strategist"}

    async def generate_strategy(self, context: Dict[str, Any]) -> AgentExecutionResult:
        """基于研究分析和风控结论生成投资策略"""
        task = f"""请基于以下分析结果，按照策略输出框架生成投资建议：

研究分析结论：
{context.get('researcher_result', '暂无研究数据')}

风险评估结论：
{context.get('risk_result', '暂无风控数据')}

用户偏好：
{context.get('user_preference', '未指定（默认平衡型）')}

请提供完整的策略方案。"""
        return await self.execute(task=task, context=context)
