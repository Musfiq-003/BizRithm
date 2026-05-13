# backend/models/dataset.py
import uuid
from sqlalchemy import Column, String, Integer, BigInteger, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.core.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(500))
    file_type = Column(String(20))
    file_size_bytes = Column(BigInteger)
    row_count = Column(Integer)
    column_count = Column(Integer)
    columns_meta = Column(JSONB)      # [{name, dtype, nulls, unique_count, sample}]
    table_name = Column(String(100))  # PostgreSQL ingested table name
    status = Column(String(50), default="pending")  # pending, processing, ready, error
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="datasets")
    sql_queries = relationship("SQLQuery", back_populates="dataset")
    predictions = relationship("MLPrediction", back_populates="dataset")
    reports = relationship("Report", back_populates="dataset")
    insights = relationship("Insight", back_populates="dataset")

    def __repr__(self):
        return f"<Dataset {self.name} ({self.status})>"
