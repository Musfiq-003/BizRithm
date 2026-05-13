# ml_models/base_model.py
"""Abstract base class for all ML forecasting models."""
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class ModelResult:
    model_name: str
    predictions: List[float]
    forecast_dates: List[str]
    metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]]
    training_time: float
    lower_bound: Optional[List[float]] = None
    upper_bound: Optional[List[float]] = None


class BaseForecaster(ABC):
    """Abstract base for all forecasting models."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.is_trained = False
        self.feature_names: List[str] = []

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> None:
        """Train the model."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate predictions."""
        pass

    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

        mae = float(mean_absolute_error(y_true, y_pred))
        mse = float(mean_squared_error(y_true, y_pred))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_true, y_pred))

        # MAPE — handle zeros gracefully
        nonzero_mask = y_true != 0
        if nonzero_mask.sum() > 0:
            mape = float(np.mean(np.abs((y_true[nonzero_mask] - y_pred[nonzero_mask]) / y_true[nonzero_mask])) * 100)
        else:
            mape = 0.0

        return {"mae": mae, "rmse": rmse, "r2": r2, "mape": mape, "mse": mse}

    def train_test_split(
        self,
        df: pd.DataFrame,
        target_col: str,
        split_ratio: float = 0.8
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Time-aware train/test split."""
        split_idx = int(len(df) * split_ratio)
        feature_cols = [c for c in df.columns if c != target_col]

        X = df[feature_cols]
        y = df[target_col]

        return X.iloc[:split_idx], X.iloc[split_idx:], y.iloc[:split_idx], y.iloc[split_idx:]
