# backend/models/insight.py
import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.core.database import Base


class Insight(Base):
    __tablename__ = "insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"))
    insight_type = Column(String(100))
    title = Column(String(255))
    content = Column(Text)
    severity = Column(String(20), default="info")
    metadata_ = Column("metadata", JSONB)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    dataset = relationship("Dataset", back_populates="insights")
