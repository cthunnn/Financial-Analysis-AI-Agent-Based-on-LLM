"""
backend/app/agents/base.py
Agent 基类框架 - 提供通用 Agent 生命周期管理和工具调用能力
"""
import uuid
import time
import logging
from typing import Dict, Any, List, Optional, AsyncIterator
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from langchain.schema import HumanMessage, SystemMessage, BaseMessage
from langchain.tools import BaseTool

from app.models.schemas import AgentType
from app.core.llm import LLMService, get_llm_service

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Agent 配置"""
    name: str
    agent_type: AgentType
    description: str
    system_prompt: str
    tools: List[BaseTool] = field(default_factory=list)
    max_iterations: int = 10
    early_stop_threshold: float = 0.8
    temperature: float = 0.7


@dataclass
class AgentExecutionResult:
    """Agent 执行结果"""
    success: bool
    output: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    total_tokens: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Agent 基类
    提供通用能力：执行管理、工具调用、输出解析、执行历史记录
    子类需实现 _build_system_prompt 和 _parse_output
    """

    def __init__(self, config: AgentConfig, llm_service: Optional[LLMService] = None):
        self.config = config
        self.llm = llm_service or get_llm_service()
        self._execution_history: List[Dict] = []
        self._memory: List[BaseMessage] = []
        logger.info(f"[Agent] {config.name} 已初始化, 工具数量={len(config.tools)}")

    @abstractmethod
    def _build_system_prompt(self) -> str:
        """构建系统提示词，子类必须实现"""
        pass

    @abstractmethod
    def _parse_output(self, raw_output: str) -> Dict[str, Any]:
        """解析LLM原始输出为结构化结果，子类必须实现"""
        pass

    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> AgentExecutionResult:
        """
        执行 Agent 任务

        Args:
            task: 任务描述
            context: 上下文数据
            session_id: 会话ID

        Returns:
            AgentExecutionResult 包含执行状态、输出和元数据
        """
        task_id = str(uuid.uuid4())
        start_time = time.time()
        total_tokens = 0

        logger.info(f"[Agent:{self.config.name}] 开始执行 task_id={task_id}")

        try:
            # 构建完整提示词
            prompt_content = self._build_system_prompt()
            if context:
                context_str = self._format_context(context)
                prompt_content += f"\n\n## 上下文信息\n{context_str}"
            prompt_content += f"\n\n## 当前任务\n{task}"

            messages = [
                SystemMessage(content=prompt_content),
                HumanMessage(content=task),
            ]

            # 工具调用
            tools_json = self._tools_to_json(self.config.tools)
            if tools_json:
                content, call_log = await self.llm.chat(
                    messages=messages, tools=tools_json, stream=False
                )
                if not call_log.success:
                    raise Exception(f"LLM 调用失败: {call_log.error}")
                total_tokens = call_log.total_tokens
                agent_output = content
            else:
                content, call_log = await self.llm.chat(
                    messages=messages, stream=False
                )
                if not call_log.success:
                    raise Exception(f"LLM 调用失败: {call_log.error}")
                total_tokens = call_log.total_tokens
                agent_output = content

            # 解析输出
            parsed = self._parse_output(agent_output)
            execution_time = (time.time() - start_time) * 1000

            # 记录执行历史
            self._execution_history.append({
                "task_id": task_id,
                "task": task,
                "output": agent_output,
                "parsed": parsed,
                "tokens": total_tokens,
                "execution_time_ms": execution_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            })

            return AgentExecutionResult(
                success=True,
                output=agent_output,
                iterations=1,
                total_tokens=total_tokens,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"[Agent:{self.config.name}] 执行失败: {str(e)}", exc_info=True)
            return AgentExecutionResult(
                success=False,
                output="",
                error=str(e),
                iterations=0,
                total_tokens=total_tokens,
                execution_time_ms=execution_time,
            )

    async def execute_stream(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """流式执行 Agent 任务"""
        prompt_content = self._build_system_prompt()
        if context:
            context_str = self._format_context(context)
            prompt_content += f"\n\n## 上下文信息\n{context_str}"
        prompt_content += f"\n\n## 当前任务\n{task}"

        messages = [
            SystemMessage(content=prompt_content),
            HumanMessage(content=task),
        ]

        full_response = ""
        async for token, _ in self.llm.chat_stream(messages):
            if token:
                full_response += token
                yield token

        logger.info(f"[Agent:{self.config.name}] 流式输出完成, 长度={len(full_response)}")

    def _format_context(self, context: Dict[str, Any]) -> str:
        """将上下文字典格式化为文本"""
        lines = []
        for key, value in context.items():
            if isinstance(value, list):
                lines.append(f"### {key}")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"- {item.get('content', str(item))[:200]}")
                    else:
                        lines.append(f"- {str(item)[:200]}")
            elif isinstance(value, dict):
                lines.append(f"### {key}")
                for k, v in value.items():
                    lines.append(f"- {k}: {str(v)[:200]}")
            else:
                lines.append(f"**{key}**: {str(value)[:500]}")
        return "\n".join(lines)

    def _tools_to_json(self, tools: List[BaseTool]) -> List[Dict]:
        """将 LangChain Tool 列表转换为 OpenAI Function Calling 格式"""
        result = []
        for tool in tools:
            result.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            })
        return result

    def get_execution_history(self) -> List[Dict]:
        """获取 Agent 执行历史"""
        return self._execution_history

    def clear_history(self) -> None:
        """清空执行历史"""
        self._execution_history.clear()
