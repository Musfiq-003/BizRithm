# backend/schemas/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[UUID] = None
    dataset_id: Optional[UUID] = None
    language: str = "en"  # en, bn


class ChatResponse(BaseModel):
    session_id: UUID
    response: str
    intent: Optional[str] = None
    sql_query: Optional[str] = None
    chart_data: Optional[Dict[str, Any]] = None
    data_preview: Optional[List[Dict]] = None
    suggestions: Optional[List[str]] = None
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None


class ChatHistoryItem(BaseModel):
    id: UUID
    role: str
    content: str
    intent: Optional[str]
    created_at: datetime
    metadata_: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ChatHistory(BaseModel):
    session_id: UUID
    messages: List[ChatHistoryItem]
    total: int
