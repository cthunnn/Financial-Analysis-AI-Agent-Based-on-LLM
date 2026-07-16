"""
backend/tests/conftest.py
Pytest 全局配置 - 异步测试支持与共享夹具
"""
import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """创建会话级事件循环供异步测试使用"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_stock_code():
    """测试用股票代码"""
    return "600519"


@pytest.fixture
def sample_query():
    """测试用分析查询"""
    return "分析贵州茅台600519的基本面和估值水平"


@pytest.fixture
def sample_risk_query():
    """测试用风险查询"""
    return "评估贵州茅台600519的投资风险"


@pytest.fixture
def mock_context():
    """测试用上下文数据"""
    return {
        "researcher_result": "基本面分析显示该公司营收稳定增长...",
        "risk_result": "综合风险评估为中等，主要风险点在于...",
        "user_preference": "稳健型投资者",
    }
