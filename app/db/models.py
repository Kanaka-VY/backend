from datetime import datetime
from sqlmodel import SQLModel, Field


class ChatMessageDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str = Field(index=True)
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)