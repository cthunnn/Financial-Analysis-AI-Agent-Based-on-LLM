"""
backend/app/agents/orchestrator.py
多Agent编排器 - 意图分类、任务调度、并行/串行执行、结果聚合
"""
import uuid
import time
import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio

from app.agents.base import AgentExecutionResult
from app.agents.researcher import ResearcherAgent
from app.agents.risk_agent import RiskAgent
from app.agents.strategist import StrategistAgent
from app.models.schemas import AgentType

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorConfig:
    """编排器配置"""
    max_parallel_agents: int = 3
    timeout_per_agent: int = 60
    enable_caching: bool = True


class AgentOrchestrator:
    """
    多Agent编排器
    核心流程：意图分类 -> Agent选择 -> 并行/串行执行 -> 结果聚合 -> 记忆管理
    """

    # 意图到Agent类型的映射表
    INTENT_AGENT_MAP = {
        "stock_analysis": [AgentType.RESEARCHER],
        "stock_risk": [AgentType.RISK],
        "full_analysis": [AgentType.RESEARCHER, AgentType.RISK, AgentType.STRATEGIST],
        "investment_advice": [AgentType.RESEARCHER, AgentType.STRATEGIST],
        "risk_warning": [AgentType.RISK],
        "report": [AgentType.RESEARCHER],
        "general": [AgentType.RESEARCHER],
    }

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self._agents: Dict[AgentType, Any] = {}
        self._session_memory: Dict[str, List[Dict]] = {}
        self._init_agents()

    def _init_agents(self) -> None:
        """初始化所有Agent实例"""
        self._agents = {
            AgentType.RESEARCHER: ResearcherAgent(),
            AgentType.RISK: RiskAgent(),
            AgentType.STRATEGIST: StrategistAgent(),
        }
        logger.info(f"[编排器] 已初始化 {len(self._agents)} 个Agent")

    def _classify_intent(self, query: str) -> str:
        """基于关键词匹配进行意图分类"""
        q = query.lower()

        # 风险评估意图
        risk_keywords = ["风险", "风险评估", "暴雷", "违约", "亏损", "预警", "下跌风险"]
        full_keywords = ["全面分析", "深度分析", "完整分析", "综合分析", "投资建议"]

        if any(k in q for k in risk_keywords):
            if any(k in q for k in full_keywords):
                return "full_analysis"
            return "stock_risk"

        # 投资策略意图
        if any(k in q for k in ["策略", "组合", "配置", "仓位", "建仓", "买入", "调仓"]):
            return "investment_advice"

        # 全面分析意图
        if any(k in q for k in full_keywords):
            return "full_analysis"

        # 报告生成意图
        if any(k in q for k in ["报告", "研报", "分析报告", "生成报告"]):
            return "report"

        # 股票分析意图
        if any(k in q for k in ["分析", "估值", "财务", "营收", "利润", "roe", "pe", "基本面"]):
            return "stock_analysis"

        return "general"

    def _extract_stock_codes(self, query: str) -> List[str]:
        """从查询中提取6位股票代码"""
        return re.findall(r'\b\d{6}\b', query)

    async def run(
        self,
        query: str,
        session_id: Optional[str] = None,
        agent_types: Optional[List[AgentType]] = None,
        parallel: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        执行多Agent编排

        Args:
            query: 用户查询
            session_id: 会话ID
            agent_types: 指定Agent类型列表
            parallel: 是否并行执行
            context: 外部上下文

        Returns:
            包含执行结果的字典
        """
        session_id = session_id or str(uuid.uuid4())
        run_id = str(uuid.uuid4())

        logger.info(f"[编排器] run_id={run_id} query={query[:50]} parallel={parallel}")

        # Step 1: 意图分类
        intent = self._classify_intent(query)
        stock_codes = self._extract_stock_codes(query)
        logger.info(f"[编排器] 意图={intent} 股票={stock_codes}")

        # Step 2: 选择Agent
        if agent_types:
            selected_agents = agent_types
        else:
            selected_agents = [
                AgentType(a) for a in self.INTENT_AGENT_MAP.get(intent, [AgentType.RESEARCHER])
            ]

        # Step 3: 执行
        agent_results: Dict[AgentType, AgentExecutionResult] = {}

        if parallel and len(selected_agents) > 1:
            # 并行执行
            tasks = []
            for agent_type in selected_agents:
                agent = self._agents.get(agent_type)
                if agent:
                    tasks.append((
                        agent_type,
                        self._run_single_agent(agent, query, stock_codes, context),
                    ))

            coros = [t for _, t in tasks]
            results = await asyncio.gather(*coros, return_exceptions=True)

            for i, (agent_type, _) in enumerate(tasks):
                result = results[i]
                if isinstance(result, Exception):
                    agent_results[agent_type] = AgentExecutionResult(
                        success=False, output="", error=str(result),
                    )
                else:
                    agent_results[agent_type] = result
        else:
            # 串行执行（支持上下文传递）
            shared_context = context or {}
            for agent_type in selected_agents:
                agent = self._agents.get(agent_type)
                if agent:
                    # 传递前序Agent的结果作为上下文
                    if agent_type == AgentType.RISK and AgentType.RESEARCHER in agent_results:
                        shared_context["researcher_result"] = agent_results[AgentType.RESEARCHER].output
                    if agent_type == AgentType.STRATEGIST:
                        if AgentType.RESEARCHER in agent_results:
                            shared_context["researcher_result"] = agent_results[AgentType.RESEARCHER].output
                        if AgentType.RISK in agent_results:
                            shared_context["risk_result"] = agent_results[AgentType.RISK].output

                    result = await self._run_single_agent(
                        agent, query, stock_codes, shared_context,
                    )
                    agent_results[agent_type] = result

        # Step 4: 结果聚合
        final_response = self._aggregate_results(query, agent_results)

        # Step 5: 记录会话记忆
        if session_id not in self._session_memory:
            self._session_memory[session_id] = []
        self._session_memory[session_id].append({
            "run_id": run_id,
            "query": query,
            "intent": intent,
            "agents_used": [a.value for a in selected_agents],
            "results": {k.value: v.output for k, v in agent_results.items()},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        # 计算汇总指标
        total_time = sum(r.execution_time_ms for r in agent_results.values())
        total_tokens = sum(r.total_tokens for r in agent_results.values())
        success_count = sum(1 for r in agent_results.values() if r.success)

        return {
            "run_id": run_id,
            "session_id": session_id,
            "intent": intent,
            "agent_results": {k.value: v.output for k, v in agent_results.items()},
            "final_response": final_response,
            "execution_summary": {
                "agents_used": [a.value for a in selected_agents],
                "parallel": parallel,
                "total_execution_ms": total_time,
                "total_tokens": total_tokens,
                "success_count": success_count,
            },
        }

    async def _run_single_agent(
        self,
        agent: Any,
        query: str,
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentExecutionResult:
        """执行单个Agent，带超时控制"""
        task = query
        if stock_codes:
            task = f"分析目标股票: {', '.join(stock_codes)}\n\n用户问题: {query}"

        try:
            return await asyncio.wait_for(
                agent.execute(task=task, context=context),
                timeout=self.config.timeout_per_agent,
            )
        except asyncio.TimeoutError:
            return AgentExecutionResult(
                success=False,
                output="",
                error=f"执行超时 (>{self.config.timeout_per_agent}s)",
            )

    def _aggregate_results(
        self,
        query: str,
        agent_results: Dict[AgentType, AgentExecutionResult],
    ) -> str:
        """聚合多个Agent的执行结果"""
        parts = []

        # 按优先级排序输出
        order = [AgentType.RESEARCHER, AgentType.RISK, AgentType.STRATEGIST]
        labels = {
            AgentType.RESEARCHER: "投研分析结果",
            AgentType.RISK: "风险评估结果",
            AgentType.STRATEGIST: "策略建议",
        }

        for agent_type in order:
            result = agent_results.get(agent_type)
            if result and result.success and result.output:
                label = labels.get(agent_type, agent_type.value)
                parts.append(f"\n## {label}\n\n{result.output}\n")

        if not parts:
            errors = [
                f"{k.value}: {v.error}"
                for k, v in agent_results.items()
                if not v.success
            ]
            return f"分析过程遇到问题: {'; '.join(errors)}"

        return "\n".join(parts)

    def get_session_memory(self, session_id: str) -> List[Dict]:
        """获取会话记忆"""
        return self._session_memory.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        """清除会话记忆"""
        if session_id in self._session_memory:
            del self._session_memory[session_id]


# 模块级单例
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """获取编排器单例"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
