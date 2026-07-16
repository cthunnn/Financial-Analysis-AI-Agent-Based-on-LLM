"""
backend/app/models/schemas.py
Pydantic 请求/响应数据模型 - API 接口的输入输出定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any, Dict
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Agent 类型枚举"""
    RESEARCHER = "researcher"
    RISK = "risk"
    STRATEGIST = "strategist"
    REPORT = "report"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ===== 对话相关模型 =====

class ChatMessage(BaseModel):
    """对话消息"""
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    agent_type: Optional[AgentType] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """对话请求"""
    session_id: str = Field(default="", description="会话ID，为空时自动创建")
    message: str = Field(..., min_length=1, max_length=4000, description="用户消息")
    agent_type: Optional[AgentType] = Field(default=None, description="指定Agent类型")
    stream: bool = Field(default=True, description="是否流式返回")
    enable_rag: bool = Field(default=True, description="是否启用RAG增强")


class ChatResponse(BaseModel):
    """对话响应"""
    session_id: str
    message: str
    agent_type: AgentType
    sources: Optional[List[Dict[str, Any]]] = None
    token_usage: Optional[Dict[str, int]] = None
    latency_ms: Optional[float] = None
    session_created: bool = False


# ===== Agent 编排相关模型 =====

class AgentInvokeRequest(BaseModel):
    """Agent 编排请求"""
    session_id: str = Field(default="", description="会话ID")
    query: str = Field(..., min_length=1, max_length=4000)
    agent_types: Optional[List[AgentType]] = Field(default=None, description="指定Agent类型列表")
    parallel: bool = Field(default=True, description="是否并行执行")


# ===== RAG 检索相关模型 =====

class RAGQueryRequest(BaseModel):
    """RAG 检索请求"""
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=10, ge=1, le=100)
    score_threshold: float = Field(default=0.5, ge=0, le=1)
    filters: Optional[Dict[str, Any]] = None
    enable_rerank: bool = Field(default=True)


class RAGQueryResponse(BaseModel):
    """RAG 检索响应"""
    query: str
    chunks: List[Dict[str, Any]]
    total_retrieved: int
    rerank_applied: bool


class KnowledgeBaseUpload(BaseModel):
    """知识库文档上传"""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=50)
    metadata: Optional[Dict[str, Any]] = None


# ===== LLMOps 监控相关模型 =====

class LLMCallRecord(BaseModel):
    """LLM 调用记录"""
    call_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost_usd: float
    success: bool
    timestamp: str
    error: Optional[str] = None


class LLMOpsMetrics(BaseModel):
    """LLMOps 指标汇总"""
    all_time: Dict[str, Any]
    today: Dict[str, Any]


# ===== 数据管道相关模型 =====

class DataPipelineRun(BaseModel):
    """数据管道运行记录"""
    run_id: str
    pipeline_name: str
    status: TaskStatus
    started_at: str
    completed_at: Optional[str] = None
    records_processed: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None


# ===== 用户认证相关模型 =====

class TokenResponse(BaseModel):
    """认证令牌响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class UserCreateRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=100)
