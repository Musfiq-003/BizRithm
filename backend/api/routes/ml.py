# backend/api/routes/ml.py
"""ML Forecasting API routes."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.logger import logger
from backend.models.user import User
from backend.models.dataset import Dataset
from backend.models.prediction import MLPrediction
from backend.schemas.ml import ForecastRequest
from backend.api.middleware.auth_middleware import get_current_user
from ml_models.model_registry import get_model_registry
from utils.data_processor import load_file, clean_dataframe

router = APIRouter()


@router.post("/forecast")
async def run_forecast(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run ML forecasting on a dataset."""
    # Load dataset
    result = await db.execute(
        select(Dataset).where(Dataset.id == request.dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    if dataset.status != "ready":
        raise HTTPException(400, f"Dataset not ready (status: {dataset.status})")

    try:
        import pandas as pd
        df = load_file(dataset.file_path)
        df = clean_dataframe(df)

        registry = get_model_registry()
        forecast_results = await registry.run_forecast_pipeline(
            df=df,
            target_col=request.target_column,
            date_col=request.date_column,
            feature_cols=request.feature_columns,
            model_names=request.model_names,
            forecast_periods=request.forecast_periods,
            split_ratio=request.train_test_split,
        )

        # Save prediction record
        pred_id = str(uuid.uuid4())
        prediction = MLPrediction(
            id=pred_id,
            user_id=current_user.id,
            dataset_id=request.dataset_id,
            model_name=forecast_results.get("best_model", "unknown"),
            target_column=request.target_column,
            feature_columns=request.feature_columns,
            forecast_periods=request.forecast_periods,
            metrics=forecast_results.get("best_metrics"),
            predictions=[
                {"date": d, "predicted": p}
                for d, p in zip(
                    forecast_results.get("forecast_dates", []),
                    forecast_results.get("predictions", []),
                )
            ],
            status="completed",
        )
        db.add(prediction)

        # Generate AI insight
        from analytics.insight_generator import get_insight_generator
        insight_gen = get_insight_generator()
        insight = await insight_gen.generate_forecast_insight(
            forecast_results, forecast_results.get("best_metrics", {})
        )

        return {
            "prediction_id": pred_id,
            "dataset_id": str(request.dataset_id),
            "target_column": request.target_column,
            "best_model": forecast_results.get("best_model"),
            "metrics": forecast_results.get("comparison", []),
            "forecast": [
                {
                    "date": d,
                    "predicted": round(p, 2),
                    "lower_bound": round(lb, 2) if lb else None,
                    "upper_bound": round(ub, 2) if ub else None,
                }
                for d, p, lb, ub in zip(
                    forecast_results.get("forecast_dates", []),
                    forecast_results.get("predictions", []),
                    forecast_results.get("lower_bound", [None] * 100),
                    forecast_results.get("upper_bound", [None] * 100),
                )
            ],
            "historical": forecast_results.get("historical", []),
            "feature_importance": forecast_results.get("feature_importance"),
            "insight": insight,
            "status": "completed",
        }

    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(500, f"Forecasting failed: {str(e)}")


@router.get("/predictions")
async def list_predictions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List ML predictions for current user."""
    result = await db.execute(
        select(MLPrediction)
        .where(MLPrediction.user_id == current_user.id)
        .order_by(MLPrediction.created_at.desc())
        .limit(20)
    )
    preds = result.scalars().all()

    return {
        "predictions": [
            {
                "id": str(p.id),
                "model_name": p.model_name,
                "target_column": p.target_column,
                "forecast_periods": p.forecast_periods,
                "metrics": p.metrics,
                "status": p.status,
                "created_at": str(p.created_at),
            }
            for p in preds
        ]
    }
