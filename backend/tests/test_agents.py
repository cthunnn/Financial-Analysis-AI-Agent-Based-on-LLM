"""
backend/tests/test_agents.py
Agent 系统测试 - 验证各Agent的创建、配置与基础执行逻辑
"""
import pytest

from app.agents.base import AgentConfig, AgentExecutionResult
from app.agents.researcher import ResearcherAgent
from app.agents.risk_agent import RiskAgent
from app.agents.strategist import StrategistAgent
from app.agents.report_agent import ReportAgent
from app.agents.orchestrator import AgentOrchestrator, OrchestratorConfig
from app.models.schemas import AgentType


class TestAgentCreation:
    """测试 Agent 的创建与配置"""

    def test_create_researcher_agent(self):
        agent = ResearcherAgent()
        assert agent.config.agent_type == AgentType.RESEARCHER
        assert agent.config.name == "投研分析Agent"
        assert len(agent.config.tools) == 4

    def test_create_risk_agent(self):
        agent = RiskAgent()
        assert agent.config.agent_type == AgentType.RISK
        assert agent.config.name == "风控预警Agent"
        assert len(agent.config.tools) == 2

    def test_create_strategist_agent(self):
        agent = StrategistAgent()
        assert agent.config.agent_type == AgentType.STRATEGIST
        assert agent.config.name == "策略生成Agent"

    def test_create_report_agent(self):
        agent = ReportAgent()
        assert agent.config.agent_type == AgentType.REPORT
        assert agent.config.name == "报告生成Agent"


class TestAgentConfig:
    """测试 Agent 配置数据类"""

    def test_agent_config_defaults(self):
        config = AgentConfig(
            name="测试Agent",
            agent_type=AgentType.RESEARCHER,
            description="测试用",
            system_prompt="你是一个测试助手",
        )
        assert config.max_iterations == 10
        assert config.early_stop_threshold == 0.8
        assert config.temperature == 0.7
        assert config.tools == []

    def test_agent_config_custom(self):
        config = AgentConfig(
            name="自定义Agent",
            agent_type=AgentType.RISK,
            description="自定义风控",
            system_prompt="自定义提示词",
            max_iterations=5,
            temperature=0.3,
        )
        assert config.max_iterations == 5
        assert config.temperature == 0.3


class TestAgentExecutionResult:
    """测试 Agent 执行结果"""

    def test_success_result(self):
        result = AgentExecutionResult(
            success=True,
            output="分析完成",
            total_tokens=100,
            execution_time_ms=500.0,
        )
        assert result.success is True
        assert result.output == "分析完成"
        assert result.error is None

    def test_failure_result(self):
        result = AgentExecutionResult(
            success=False,
            output="",
            error="模型调用超时",
        )
        assert result.success is False
        assert result.error == "模型调用超时"


class TestOrchestrator:
    """测试编排器"""

    def test_create_orchestrator(self):
        orchestrator = AgentOrchestrator()
        assert orchestrator is not None
        assert len(orchestrator._agents) == 3  # researcher, risk, strategist

    def test_classify_intent_stock_analysis(self, sample_query):
        orchestrator = AgentOrchestrator()
        intent = orchestrator._classify_intent(sample_query)
        assert intent == "stock_analysis"

    def test_classify_intent_risk(self, sample_risk_query):
        orchestrator = AgentOrchestrator()
        intent = orchestrator._classify_intent(sample_risk_query)
        assert intent == "stock_risk"

    def test_classify_intent_full_analysis(self):
        orchestrator = AgentOrchestrator()
        intent = orchestrator._classify_intent("对600519进行全面的深度分析")
        assert intent == "full_analysis"

    def test_classify_intent_investment_advice(self):
        orchestrator = AgentOrchestrator()
        intent = orchestrator._classify_intent("请给一个科技板块的仓位配置建议")
        assert intent == "investment_advice"

    def test_extract_stock_codes(self):
        orchestrator = AgentOrchestrator()
        codes = orchestrator._extract_stock_codes("分析600519和000858的基本面")
        assert "600519" in codes
        assert "000858" in codes

    def test_extract_no_stock_codes(self):
        orchestrator = AgentOrchestrator()
        codes = orchestrator._extract_stock_codes("今天大盘怎么样")
        assert codes == []


class TestOrchestratorConfig:
    """测试编排器配置"""

    def test_default_config(self):
        config = OrchestratorConfig()
        assert config.max_parallel_agents == 3
        assert config.timeout_per_agent == 60
        assert config.enable_caching is True

    def test_custom_config(self):
        config = OrchestratorConfig(
            max_parallel_agents=5,
            timeout_per_agent=120,
        )
        assert config.max_parallel_agents == 5
        assert config.timeout_per_agent == 120
