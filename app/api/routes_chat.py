import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from openai import AuthenticationError, APIError

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    HistoryResponse,
    ConversationSummary,
    ConversationListResponse,
)
from app.services.llm_service import generate_reply
from app.db.database import get_session
from app.db.models import ChatMessageDB

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, session: Session = Depends(get_session)):
    try:
        conversation_id = payload.conversation_id or str(uuid.uuid4())

        # Save user messages (only the last user message is enough for minimal demo,
        # but we save all provided for consistency)
        for msg in payload.messages:
            session.add(
                ChatMessageDB(
                    conversation_id=conversation_id,
                    role=msg.role,
                    content=msg.content,
                )
            )

        reply_text = generate_reply(payload.messages)

        session.add(
            ChatMessageDB(
                conversation_id=conversation_id,
                role="assistant",
                content=reply_text,
            )
        )
        session.commit()

        return ChatResponse(reply=reply_text, conversation_id=conversation_id)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid Groq API key: {str(exc)}")
    except APIError as exc:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(exc)}")


@router.get("/chat/{conversation_id}", response_model=HistoryResponse)
def get_chat_history(conversation_id: str, session: Session = Depends(get_session)):
    rows = session.exec(
        select(ChatMessageDB)
        .where(ChatMessageDB.conversation_id == conversation_id)
        .order_by(ChatMessageDB.created_at)
    ).all()

    messages = [
        ChatMessage(
            role=row.role,
            content=row.content,
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]
    return HistoryResponse(conversation_id=conversation_id, messages=messages)


@router.get("/conversations", response_model=ConversationListResponse)
def list_conversations(session: Session = Depends(get_session)):
    rows = session.exec(
        select(ChatMessageDB).order_by(ChatMessageDB.created_at.desc())
    ).all()

    seen_ids: set[str] = set()
    summaries: list[ConversationSummary] = []
    for row in rows:
        if row.conversation_id in seen_ids:
            continue
        seen_ids.add(row.conversation_id)
        summaries.append(
            ConversationSummary(
                conversation_id=row.conversation_id,
                preview=(row.content[:60] + "...") if len(row.content) > 60 else row.content,
                updated_at=row.created_at.isoformat(),
            )
        )

    return ConversationListResponse(conversations=summaries[:30])