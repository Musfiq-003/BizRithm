# backend/api/routes/chat.py
"""AI Chat endpoint."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.logger import logger
from backend.models.user import User
from backend.models.dataset import Dataset
from backend.models.chat_message import ChatMessage
from backend.schemas.chat import ChatRequest, ChatResponse, ChatHistory
from backend.api.middleware.auth_middleware import get_current_user
from agents.chat_agent import get_chat_agent

router = APIRouter()


@router.post("", response_model=dict)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI business consultant."""
    agent = get_chat_agent()

    # Build dataset context if provided
    dataset_context = None
    if request.dataset_id:
        result = await db.execute(
            select(Dataset).where(Dataset.id == request.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if dataset:
            dataset_context = {
                "dataset_name": dataset.name,
                "table_name": dataset.table_name,
                "columns": [c["name"] for c in (dataset.columns_meta or [])],
                "row_count": dataset.row_count,
            }

    # Process with agent
    session_id = str(request.session_id) if request.session_id else None
    result = await agent.chat(
        message=request.message,
        session_id=session_id,
        dataset_context=dataset_context,
        user_info={"full_name": current_user.full_name, "email": current_user.email},
    )

    # Persist messages
    session_uuid = uuid.UUID(result["session_id"])
    user_msg = ChatMessage(
        user_id=current_user.id,
        session_id=session_uuid,
        role="user",
        content=request.message,
        intent=result.get("intent"),
    )
    assistant_msg = ChatMessage(
        user_id=current_user.id,
        session_id=session_uuid,
        role="assistant",
        content=result.get("response", ""),
        intent=result.get("intent"),
    )
    db.add(user_msg)
    db.add(assistant_msg)

    return result


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get chat history for a session."""
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.user_id == current_user.id,
            ChatMessage.session_id == session_id,
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    messages = result.scalars().all()

    return {
        "session_id": session_id,
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "intent": m.intent,
                "created_at": str(m.created_at),
            }
            for m in messages
        ],
        "total": len(messages),
    }


@router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Clear a chat session."""
    agent = get_chat_agent()
    agent.clear_session(session_id)
    return {"message": "Session cleared"}
