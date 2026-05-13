# backend/schemas/ml.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class ForecastRequest(BaseModel):
    dataset_id: UUID
    target_column: str
    date_column: Optional[str] = None
    feature_columns: Optional[List[str]] = None
    model_names: List[str] = Field(
        default=["linear_regression", "random_forest", "xgboost", "prophet"]
    )
    forecast_periods: int = Field(default=30, ge=1, le=365)
    train_test_split: float = Field(default=0.8, ge=0.5, le=0.95)


class ModelMetrics(BaseModel):
    model_name: str
    mae: float
    rmse: float
    r2: float
    mape: Optional[float]
    training_time_seconds: float


class PredictionPoint(BaseModel):
    date: str
    predicted: float
    lower_bound: Optional[float]
    upper_bound: Optional[float]


class ForecastResponse(BaseModel):
    prediction_id: UUID
    dataset_id: UUID
    target_column: str
    best_model: str
    metrics: List[ModelMetrics]
    forecast: List[PredictionPoint]
    historical: List[Dict[str, Any]]
    feature_importance: Optional[Dict[str, float]]
    insight: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChurnPredictionRequest(BaseModel):
    dataset_id: UUID
    customer_id_column: str
    target_column: str
    feature_columns: Optional[List[str]] = None
