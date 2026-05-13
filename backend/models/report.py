# backend/models/report.py
import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(100))
    file_path = Column(String(500))
    file_size_bytes = Column(Integer)
    config = Column(JSONB)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reports")
    dataset = relationship("Dataset", back_populates="reports")
