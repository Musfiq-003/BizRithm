# analytics/anomaly_detector.py
"""Statistical anomaly detection for business data."""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from scipy import stats


def detect_zscore_anomalies(
    series: pd.Series,
    threshold: float = 2.5,
    window: Optional[int] = None
) -> pd.Series:
    """Detect anomalies using Z-score method."""
    if window:
        mean = series.rolling(window=window, min_periods=1).mean()
        std = series.rolling(window=window, min_periods=1).std()
        z_scores = (series - mean) / (std + 1e-8)
    else:
        z_scores = np.abs(stats.zscore(series.dropna()))
        z_series = pd.Series(index=series.dropna().index, data=z_scores)
        z_scores = z_series.reindex(series.index)

    return z_scores.abs() > threshold


def detect_iqr_anomalies(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """Detect anomalies using IQR method."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR
    return (series < lower) | (series > upper)


def detect_all_anomalies(
    df: pd.DataFrame,
    numeric_columns: Optional[List[str]] = None,
    date_col: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Detect anomalies across all numeric columns."""
    anomalies = []

    if numeric_columns is None:
        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()

    for col in numeric_columns:
        series = df[col].dropna()
        if len(series) < 5:
            continue

        zscore_mask = detect_zscore_anomalies(series)
        iqr_mask = detect_iqr_anomalies(series)

        # Points flagged by both methods are high-confidence anomalies
        combined = zscore_mask & iqr_mask.reindex(zscore_mask.index, fill_value=False)
        anomaly_points = df[combined.reindex(df.index, fill_value=False)]

        if len(anomaly_points) > 0:
            for _, row in anomaly_points.iterrows():
                anomaly = {
                    "column": col,
                    "value": float(row[col]),
                    "mean": float(series.mean()),
                    "std": float(series.std()),
                    "z_score": abs(float((row[col] - series.mean()) / (series.std() + 1e-8))),
                    "severity": "high" if abs((row[col] - series.mean()) / (series.std() + 1e-8)) > 3 else "medium",
                }
                if date_col and date_col in row.index:
                    anomaly["date"] = str(row[date_col])
                anomalies.append(anomaly)

    # Sort by severity and z-score
    anomalies.sort(key=lambda x: (-int(x["severity"] == "high"), -x["z_score"]))
    return anomalies[:20]  # Top 20 anomalies


def detect_sudden_changes(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    threshold_pct: float = 30.0
) -> List[Dict[str, Any]]:
    """Detect sudden percentage changes in time series."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col)
    df["month"] = df[date_col].dt.to_period("M")

    monthly = df.groupby("month")[value_col].sum()
    pct_changes = monthly.pct_change() * 100

    sudden = []
    for period, change in pct_changes.items():
        if abs(change) >= threshold_pct:
            sudden.append({
                "period": str(period),
                "change_pct": round(float(change), 2),
                "direction": "spike" if change > 0 else "drop",
                "value": float(monthly[period]),
                "severity": "high" if abs(change) >= 50 else "medium",
            })

    return sorted(sudden, key=lambda x: -abs(x["change_pct"]))
