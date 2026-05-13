# backend/models/prediction.py
import uuid
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.core.database import Base


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"))
    model_name = Column(String(100), nullable=False)
    target_column = Column(String(100), nullable=False)
    feature_columns = Column(JSONB)
    forecast_periods = Column(Integer)
    metrics = Column(JSONB)        # {mae, rmse, r2, mape}
    predictions = Column(JSONB)    # [{date, value, lower, upper}]
    model_path = Column(String(500))
    training_time_seconds = Column(Float)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="predictions")
    dataset = relationship("Dataset", back_populates="predictions")


# backend/models/report.py
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


# backend/models/insight.py
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
