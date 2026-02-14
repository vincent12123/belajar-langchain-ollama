# models/websocket.py
# Model untuk komunikasi WebSocket real-time

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class WSMessageType(str, Enum):
    """Tipe pesan WebSocket"""
    CHAT = "chat"
    TYPING = "typing"
    ERROR = "error"
    SYSTEM = "system"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class WSIncomingMessage(BaseModel):
    """Pesan masuk dari client WebSocket"""
    type: WSMessageType = WSMessageType.CHAT
    content: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WSOutgoingMessage(BaseModel):
    """Pesan keluar ke client WebSocket"""
    type: WSMessageType
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[Any] = None
    is_final: bool = True  # False jika streaming
    error: Optional[str] = None
