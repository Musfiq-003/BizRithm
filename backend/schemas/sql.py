# backend/schemas/sql.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class NL2SQLRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    dataset_id: Optional[UUID] = None
    table_name: Optional[str] = None
    execute: bool = True
    limit: int = Field(default=100, ge=1, le=10000)


class NL2SQLResponse(BaseModel):
    query_id: UUID
    natural_language: str
    generated_sql: str
    explanation: str
    results: Optional[List[Dict[str, Any]]] = None
    row_count: Optional[int] = None
    execution_time_ms: Optional[int] = None
    chart_suggestion: Optional[str] = None
    status: str


class SQLQueryHistory(BaseModel):
    id: UUID
    natural_language: str
    generated_sql: str
    row_count: Optional[int]
    execution_time_ms: Optional[int]
    status: str
    is_bookmarked: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SQLExecuteRequest(BaseModel):
    sql: str = Field(..., min_length=5)
    dataset_id: Optional[UUID] = None
    limit: int = Field(default=100, ge=1, le=10000)


# backend/schemas/report.py
class ReportRequest(BaseModel):
    dataset_id: UUID
    title: str = Field(..., min_length=3, max_length=255)
    report_type: str = "comprehensive"  # executive, revenue, forecast, comprehensive
    include_charts: bool = True
    include_forecasts: bool = True
    include_recommendations: bool = True
    date_range_days: int = Field(default=90, ge=7, le=365)


class ReportResponse(BaseModel):
    id: UUID
    title: str
    report_type: str
    status: str
    file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
