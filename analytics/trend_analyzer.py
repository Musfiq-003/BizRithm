# analytics/trend_analyzer.py
"""Business trend detection and analysis."""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from scipy import stats


def detect_trend_direction(values: List[float]) -> Dict[str, Any]:
    """Detect if a series is trending up, down, or flat."""
    if len(values) < 3:
        return {"direction": "insufficient_data", "slope": 0, "confidence": 0}

    x = np.arange(len(values))
    y = np.array(values)

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    direction = "up" if slope > 0 else "down" if slope < 0 else "flat"
    confidence = abs(r_value) * 100

    return {
        "direction": direction,
        "slope": float(slope),
        "r_squared": float(r_value ** 2),
        "confidence": round(confidence, 1),
        "p_value": float(p_value),
        "is_significant": p_value < 0.05,
    }


def calculate_moving_average(series: pd.Series, window: int = 7) -> pd.Series:
    """Calculate rolling moving average."""
    return series.rolling(window=window, min_periods=1).mean()


def detect_seasonality(df: pd.DataFrame, date_col: str, value_col: str) -> Dict[str, Any]:
    """Detect seasonal patterns in time series data."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col)

    df["month"] = df[date_col].dt.month
    df["day_of_week"] = df[date_col].dt.dayofweek
    df["quarter"] = df[date_col].dt.quarter

    monthly_avg = df.groupby("month")[value_col].mean()
    dow_avg = df.groupby("day_of_week")[value_col].mean()
    quarterly_avg = df.groupby("quarter")[value_col].mean()

    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    dow_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    return {
        "monthly_pattern": {month_names[i-1]: float(v) for i, v in monthly_avg.items()},
        "day_of_week_pattern": {dow_names[i]: float(v) for i, v in dow_avg.items()},
        "quarterly_pattern": {f"Q{i}": float(v) for i, v in quarterly_avg.items()},
        "peak_month": month_names[int(monthly_avg.idxmax()) - 1],
        "worst_month": month_names[int(monthly_avg.idxmin()) - 1],
        "peak_day": dow_names[int(dow_avg.idxmax())],
    }


def calculate_growth_rates(df: pd.DataFrame, date_col: str, value_col: str) -> Dict[str, Any]:
    """Calculate various growth rate metrics."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col)
    df["month"] = df[date_col].dt.to_period("M")

    monthly = df.groupby("month")[value_col].sum()

    if len(monthly) < 2:
        return {}

    mom_growth = monthly.pct_change() * 100
    rolling_3m = monthly.rolling(3).mean().pct_change() * 100

    return {
        "mom_growth_rates": {str(p): round(float(v), 2) for p, v in mom_growth.items() if not np.isnan(v)},
        "rolling_3m_growth": {str(p): round(float(v), 2) for p, v in rolling_3m.items() if not np.isnan(v)},
        "avg_monthly_growth": float(mom_growth.mean()),
        "max_growth_month": str(mom_growth.idxmax()),
        "min_growth_month": str(mom_growth.idxmin()),
        "trend": detect_trend_direction(monthly.tolist()),
    }


def find_top_performers(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    top_n: int = 5
) -> Tuple[List[Dict], List[Dict]]:
    """Find top and bottom performers by category."""
    grouped = df.groupby(category_col)[value_col].sum().reset_index()
    grouped.columns = [category_col, "value"]
    grouped = grouped.sort_values("value", ascending=False)

    top = grouped.head(top_n).to_dict(orient="records")
    bottom = grouped.tail(top_n).to_dict(orient="records")

    return top, bottom
