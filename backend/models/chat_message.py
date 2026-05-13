# backend/models/chat_message.py
import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.core.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    intent = Column(String(100))
    metadata_ = Column("metadata", JSONB)
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chat_messages")
