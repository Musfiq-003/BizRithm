# backend/api/routes/insights.py
"""Business Insights API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.models.user import User
from backend.models.dataset import Dataset
from backend.api.middleware.auth_middleware import get_current_user
from analytics.kpi_calculator import calculate_revenue_kpis, calculate_product_kpis, calculate_regional_kpis, calculate_customer_kpis
from analytics.trend_analyzer import calculate_growth_rates, detect_seasonality, find_top_performers
from analytics.anomaly_detector import detect_all_anomalies, detect_sudden_changes
from analytics.insight_generator import get_insight_generator
from analytics.recommendation_engine import get_recommendation_engine
from utils.data_processor import load_file, clean_dataframe, detect_numeric_columns, detect_date_columns

router = APIRouter()


@router.get("/{dataset_id}/dashboard")
async def get_dashboard_insights(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive dashboard insights for a dataset."""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    try:
        df = load_file(dataset.file_path)
        df = clean_dataframe(df)

        numeric_cols = detect_numeric_columns(df)
        date_cols = detect_date_columns(df)

        date_col = date_cols[0] if date_cols else None
        revenue_col = next(
            (c for c in numeric_cols if any(kw in c.lower() for kw in ["revenue", "sales", "amount", "price", "total"])),
            numeric_cols[0] if numeric_cols else None,
        )

        response = {
            "dataset_id": dataset_id,
            "dataset_name": dataset.name,
            "summary": {
                "rows": len(df),
                "columns": len(df.columns),
                "numeric_columns": numeric_cols,
                "date_columns": [str(c) for c in date_cols],
            },
            "kpis": {},
            "trends": {},
            "anomalies": [],
            "recommendations": [],
            "insights_text": "",
        }

        if revenue_col:
            response["kpis"] = calculate_revenue_kpis(df, revenue_col, date_col)

            if date_col:
                response["trends"] = calculate_growth_rates(df, date_col, revenue_col)

            # Anomalies
            response["anomalies"] = detect_all_anomalies(df, numeric_cols[:5], date_col)

            # AI Insights
            gen = get_insight_generator()
            response["insights_text"] = await gen.generate_kpi_insights(
                response["kpis"],
                f"Dataset: {dataset.name}"
            )

            # Recommendations
            rec_engine = get_recommendation_engine()
            response["recommendations"] = rec_engine.generate_recommendations(
                response["kpis"],
                response["anomalies"],
                response["trends"],
            )

        return response

    except Exception as e:
        raise HTTPException(500, f"Insights failed: {str(e)}")


@router.get("/{dataset_id}/kpis")
async def get_kpis(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get KPI metrics for a dataset."""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    df = load_file(dataset.file_path)
    df = clean_dataframe(df)
    numeric_cols = detect_numeric_columns(df)
    date_cols = detect_date_columns(df)

    date_col = date_cols[0] if date_cols else None
    revenue_col = next(
        (c for c in numeric_cols if any(kw in c.lower() for kw in ["revenue", "sales", "amount", "total"])),
        numeric_cols[0] if numeric_cols else None,
    )

    if not revenue_col:
        return {"kpis": {}, "message": "No numeric revenue column found"}

    return {"kpis": calculate_revenue_kpis(df, revenue_col, date_col)}
