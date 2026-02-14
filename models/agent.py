# models/agent.py
# Model untuk AI agent, tool calling, dan chat history

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Tool Definitions ──────────────────────────────────

class ToolParameter(BaseModel):
    """Definisi satu parameter tool"""
    name: str
    type: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    default: Optional[Any] = None


class ToolDefinition(BaseModel):
    """Definisi satu tool untuk function calling"""
    name: str
    description: str
    parameters: List[ToolParameter]
    category: Optional[str] = None  # "database", "analysis", "report"


# ── Tool Call & Result ────────────────────────────────

class ToolCall(BaseModel):
    """Representasi satu pemanggilan tool oleh LLM"""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None


class ToolResult(BaseModel):
    """Hasil eksekusi satu tool"""
    call_id: Optional[str] = None
    tool_name: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


# ── Agent Interaction ─────────────────────────────────

class AgentInput(BaseModel):
    """Input untuk agent"""
    user_message: str
    session_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = []
    context: Optional[Dict[str, Any]] = None
    max_tool_calls: int = 5


class AgentStep(BaseModel):
    """Satu langkah dalam proses agent"""
    step_number: int
    action: str  # "thinking", "tool_call", "response"
    tool_call: Optional[ToolCall] = None
    tool_result: Optional[ToolResult] = None
    reasoning: Optional[str] = None


class AgentOutput(BaseModel):
    """Output keseluruhan dari agent"""
    response: str
    steps: List[AgentStep] = []
    total_tool_calls: int = 0
    data: Optional[Any] = None
    suggestions: Optional[List[str]] = None
    processing_time_ms: Optional[float] = None


# ── Chat History ──────────────────────────────────────

class ChatMessage(BaseModel):
    """Satu pesan dalam riwayat chat"""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_calls: Optional[List[ToolCall]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatSession(BaseModel):
    """Satu sesi percakapan"""
    session_id: str
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    context: Optional[Dict[str, Any]] = None
