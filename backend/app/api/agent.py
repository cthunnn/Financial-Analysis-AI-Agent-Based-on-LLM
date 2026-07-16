"""
backend/app/api/agent.py
Agent 编排 API - 多Agent协同调用的管理接口
"""
import uuid
import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import AgentInvokeRequest, AgentType
from app.agents.orchestrator import get_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/agent/invoke")
async def invoke_agent(request: AgentInvokeRequest):
    """调用多Agent编排器执行分析任务"""
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.run(
            query=request.query,
            session_id=request.session_id or str(uuid.uuid4()),
            agent_types=request.agent_types,
            parallel=request.parallel,
        )
        return {
            "run_id": result["run_id"],
            "session_id": result["session_id"],
            "intent": result["intent"],
            "final_response": result["final_response"],
            "execution_summary": result["execution_summary"],
        }
    except Exception as e:
        logger.error(f"[Agent API] 调用失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/memory/{session_id}")
async def get_session_memory(session_id: str):
    """获取指定会话的交互记忆"""
    orchestrator = get_orchestrator()
    memory = orchestrator.get_session_memory(session_id)
    return {
        "session_id": session_id,
        "conversation_turns": len(memory),
        "memory": memory,
    }


@router.delete("/agent/memory/{session_id}")
async def clear_session_memory(session_id: str):
    """清除指定会话的交互记忆"""
    orchestrator = get_orchestrator()
    orchestrator.clear_session(session_id)
    return {"message": "会话记忆已清除", "session_id": session_id}


@router.get("/agent/types")
async def list_agent_types():
    """获取可用的Agent类型列表及其能力描述"""
    return {
        "agents": [
            {
                "type": "researcher",
                "name": "投研分析Agent",
                "description": "负责股票基本面分析、财务解读与估值研判",
                "capabilities": ["stock_analysis", "financial_report", "valuation"],
            },
            {
                "type": "risk",
                "name": "风控预警Agent",
                "description": "负责风险识别、量化评估与预警监控",
                "capabilities": ["risk_assessment", "risk_warning", "compliance_check"],
            },
            {
                "type": "strategist",
                "name": "策略生成Agent",
                "description": "负责投资策略制定、组合建议与交易方案设计",
                "capabilities": ["strategy_generation", "portfolio_management", "asset_allocation"],
            },
            {
                "type": "report",
                "name": "报告生成Agent",
                "description": "负责自动生成结构化的投研分析报告",
                "capabilities": ["report_generation", "document_formatting"],
            },
        ]
    }
