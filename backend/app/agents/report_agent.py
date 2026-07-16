"""
backend/app/agents/report_agent.py
报告生成 Agent - 负责自动生成结构化的投研分析报告
"""
from typing import Dict, Any

from app.agents.base import BaseAgent, AgentConfig, AgentExecutionResult
from app.models.schemas import AgentType


# ===== Agent 提示词 =====

REPORT_SYSTEM_PROMPT = """你是一位专业金融研究报告撰写专家，擅长将复杂分析转化为清晰易读的研究报告。

报告结构框架：
1. 执行摘要（200字以内）：核心结论与投资建议要点
2. 公司概况：主营业务概述、行业地位、核心竞争力
3. 基本面分析：营收结构、利润趋势、现金流状况
4. 估值分析：当前PE/PB/PS估值水平，与历史及同行业对比
5. 风险因素：按重要性排列的主要风险项
6. 投资建议：给出买入/持有/减持建议及目标价位

格式要求：
- 使用 Markdown 结构化格式
- 关键数据以表格形式呈现
- 核心结论使用**加粗**标注
- 数据需标明来源和时间
- 报告末尾附免责声明"""


class ReportAgent(BaseAgent):
    """报告Agent：负责生成结构化投研分析报告"""

    def __init__(self):
        config = AgentConfig(
            name="报告生成Agent",
            agent_type=AgentType.REPORT,
            description="自动生成结构化投研分析报告",
            system_prompt=REPORT_SYSTEM_PROMPT,
            tools=[],
            max_iterations=3,
        )
        super().__init__(config)

    def _build_system_prompt(self) -> str:
        return self.config.system_prompt

    def _parse_output(self, raw_output: str) -> Dict[str, Any]:
        return {"report": raw_output, "agent_type": "report"}

    async def generate_report(
        self, stock_code: str, analysis_data: Dict[str, Any]
    ) -> AgentExecutionResult:
        """生成指定股票的完整投研报告"""
        task = (
            f"请为股票 {stock_code} 生成一份完整的投研分析报告。"
            f"请严格按照报告结构框架逐项撰写。"
            f"以下为已有的分析数据供参考：\n{analysis_data}"
        )
        return await self.execute(task=task)
