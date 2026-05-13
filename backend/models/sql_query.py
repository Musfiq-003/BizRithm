# backend/models/sql_query.py
import uuid
from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.core.database import Base


class SQLQuery(Base):
    __tablename__ = "sql_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    natural_language = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=False)
    execution_time_ms = Column(Integer)
    row_count = Column(Integer)
    status = Column(String(50), default="success")  # success, error, timeout
    error_message = Column(Text)
    result_preview = Column(JSONB)  # First 10 rows as JSON
    is_bookmarked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="sql_queries")
    dataset = relationship("Dataset", back_populates="sql_queries")


# backend/models/chat_message.py
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    intent = Column(String(100))  # sql, forecast, insight, general
    metadata_ = Column("metadata", JSONB)  # charts, sql, result data
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chat_messages")
