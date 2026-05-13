# ml_models/feature_engineering.py
"""Feature engineering for time series and tabular data."""
import pandas as pd
import numpy as np
from typing import Optional, List, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder


def create_time_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Create temporal features from a date column."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month
    df["day"] = df[date_col].dt.day
    df["day_of_week"] = df[date_col].dt.dayofweek
    df["day_of_year"] = df[date_col].dt.dayofyear
    df["week_of_year"] = df[date_col].dt.isocalendar().week.astype(int)
    df["quarter"] = df[date_col].dt.quarter
    df["is_weekend"] = (df[date_col].dt.dayofweek >= 5).astype(int)
    df["is_month_start"] = df[date_col].dt.is_month_start.astype(int)
    df["is_month_end"] = df[date_col].dt.is_month_end.astype(int)

    # Cyclical encoding for month and day_of_week
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

    return df


def create_lag_features(
    df: pd.DataFrame,
    target_col: str,
    lags: List[int] = [1, 7, 14, 30]
) -> pd.DataFrame:
    """Create lag features for time series."""
    df = df.copy()
    for lag in lags:
        df[f"{target_col}_lag_{lag}"] = df[target_col].shift(lag)
    return df


def create_rolling_features(
    df: pd.DataFrame,
    target_col: str,
    windows: List[int] = [7, 14, 30]
) -> pd.DataFrame:
    """Create rolling statistics features."""
    df = df.copy()
    for w in windows:
        df[f"{target_col}_rolling_mean_{w}"] = df[target_col].rolling(w, min_periods=1).mean()
        df[f"{target_col}_rolling_std_{w}"] = df[target_col].rolling(w, min_periods=1).std()
        df[f"{target_col}_rolling_max_{w}"] = df[target_col].rolling(w, min_periods=1).max()
        df[f"{target_col}_rolling_min_{w}"] = df[target_col].rolling(w, min_periods=1).min()
    return df


def encode_categoricals(df: pd.DataFrame, categorical_cols: List[str]) -> Tuple[pd.DataFrame, dict]:
    """Label encode categorical columns."""
    df = df.copy()
    encoders = {}
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
    return df, encoders


def prepare_tabular_features(
    df: pd.DataFrame,
    target_col: str,
    date_col: Optional[str] = None,
    feature_cols: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Full feature preparation pipeline."""
    df = df.copy().dropna(subset=[target_col])

    if date_col and date_col in df.columns:
        df = create_time_features(df, date_col)

    # Select feature columns
    if feature_cols is None:
        exclude = {target_col}
        if date_col:
            exclude.add(date_col)
        feature_cols = [c for c in df.columns if c not in exclude]

    # Encode categoricals
    cat_cols = df[feature_cols].select_dtypes(include="object").columns.tolist()
    if cat_cols:
        df, _ = encode_categoricals(df, cat_cols)

    X = df[feature_cols].fillna(0)
    y = df[target_col]

    return X, y
