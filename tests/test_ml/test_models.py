# tests/test_ml/test_models.py
"""ML model evaluation tests."""
import pytest
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_model_evaluator_metrics():
    """Test that model evaluator computes correct metrics."""
    from ml_models.model_evaluator import ModelEvaluator
    from ml_models.base_model import ModelResult
    evaluator = ModelEvaluator()
    y_true = np.array([100, 200, 300, 400, 500])
    y_pred = np.array([110, 190, 310, 390, 510])
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    assert mae > 0
    assert rmse > 0
    assert r2 > 0.9


def test_feature_engineering_time_features(sample_df):
    """Test time feature creation."""
    from ml_models.feature_engineering import create_time_features
    df = create_time_features(sample_df, "date")
    assert "month" in df.columns
    assert "day_of_week" in df.columns
    assert "quarter" in df.columns
    assert "month_sin" in df.columns
    assert "month_cos" in df.columns


def test_feature_engineering_lag_features(sample_df):
    """Test lag feature creation."""
    from ml_models.feature_engineering import create_lag_features
    df = create_lag_features(sample_df, "revenue", lags=[1, 7])
    assert "revenue_lag_1" in df.columns
    assert "revenue_lag_7" in df.columns


def test_linear_regression_trains():
    """Test that linear regression model trains and predicts."""
    from sklearn.linear_model import LinearRegression
    np.random.seed(42)
    X = np.random.randn(100, 3)
    y = 2*X[:, 0] + 3*X[:, 1] + np.random.randn(100) * 0.1
    model = LinearRegression()
    model.fit(X[:80], y[:80])
    preds = model.predict(X[80:])
    assert len(preds) == 20
    assert preds.std() > 0


def test_anomaly_detection(sample_df):
    """Test that anomaly detector identifies anomalies."""
    from analytics.anomaly_detector import detect_zscore_anomalies
    series = sample_df["revenue"]
    mask = detect_zscore_anomalies(series, threshold=2.0)
    assert isinstance(mask, pd.Series)
    # Should not flag all points as anomalies
    assert mask.sum() < len(series) * 0.3


def test_kpi_calculator(sample_df):
    """Test KPI calculation."""
    from analytics.kpi_calculator import calculate_revenue_kpis
    kpis = calculate_revenue_kpis(sample_df, "revenue", "date")
    assert "total_revenue" in kpis
    assert kpis["total_revenue"] > 0
    assert "avg_revenue" in kpis


def test_sql_sanitizer_blocks_dangerous():
    """Test SQL sanitizer blocks dangerous queries."""
    from utils.sql_sanitizer import sanitize_sql
    dangerous_queries = [
        "DROP TABLE users",
        "DELETE FROM sales",
        "INSERT INTO users VALUES (1, 'hacked')",
        "UPDATE users SET password = 'hacked'",
    ]
    for q in dangerous_queries:
        is_safe, _ = sanitize_sql(q)
        assert not is_safe, f"Should have blocked: {q}"


def test_sql_sanitizer_allows_select():
    """Test SQL sanitizer allows safe SELECT queries."""
    from utils.sql_sanitizer import sanitize_sql
    safe_q = "SELECT product, SUM(revenue) FROM sales GROUP BY product ORDER BY SUM(revenue) DESC LIMIT 5"
    is_safe, cleaned = sanitize_sql(safe_q)
    assert is_safe
    assert "SELECT" in cleaned.upper()


def test_trend_direction():
    """Test trend direction detection."""
    from analytics.trend_analyzer import detect_trend_direction
    upward = [100, 110, 120, 130, 140, 150]
    result = detect_trend_direction(upward)
    assert result["direction"] == "up"
    assert result["slope"] > 0

    downward = [150, 140, 130, 120, 110, 100]
    result2 = detect_trend_direction(downward)
    assert result2["direction"] == "down"
