from pydantic import BaseModel, Field
from typing import Literal, List, Optional


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)
    created_at: Optional[str] = None


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str


class HistoryResponse(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]


class ConversationSummary(BaseModel):
    conversation_id: str
    preview: str
    updated_at: str


class ConversationListResponse(BaseModel):
    conversations: List[ConversationSummary]