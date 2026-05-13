# ml_models/model_registry.py
"""ML model registry for training, saving, and loading models."""
import os
import time
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.core.config import settings
from backend.core.logger import logger
from ml_models.base_model import ModelResult
from ml_models.feature_engineering import prepare_tabular_features
from ml_models.model_evaluator import get_evaluator

os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)


class ModelRegistry:
    """Manages the full lifecycle of ML models."""

    async def run_forecast_pipeline(
        self,
        df: pd.DataFrame,
        target_col: str,
        date_col: Optional[str],
        feature_cols: Optional[List[str]],
        model_names: List[str],
        forecast_periods: int,
        split_ratio: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Full pipeline:
        1. Feature engineering
        2. Train-test split
        3. Train all requested models
        4. Evaluate and compare
        5. Generate future forecast
        """
        logger.info(f"Starting forecast pipeline for target={target_col}, models={model_names}")

        X, y = prepare_tabular_features(df, target_col, date_col, feature_cols)

        # Train/test split
        split_idx = int(len(X) * split_ratio)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        results: List[ModelResult] = []

        for model_name in model_names:
            try:
                result = await self._train_model(
                    model_name, X_train, X_test, y_train, y_test,
                    df, date_col, target_col, forecast_periods
                )
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Model {model_name} failed: {e}")

        if not results:
            raise ValueError("All models failed to train")

        evaluator = get_evaluator()
        comparison = evaluator.compare_models(results)

        # Historical data for chart
        historical = []
        if date_col and date_col in df.columns:
            hist_df = df[[date_col, target_col]].copy()
            hist_df[date_col] = pd.to_datetime(hist_df[date_col], errors="coerce")
            hist_df = hist_df.dropna().sort_values(date_col)
            historical = [
                {"date": str(row[date_col].date()), "actual": float(row[target_col])}
                for _, row in hist_df.iterrows()
            ]

        return {**comparison, "historical": historical}

    async def _train_model(
        self,
        model_name: str,
        X_train, X_test, y_train, y_test,
        df, date_col, target_col, forecast_periods
    ) -> Optional[ModelResult]:
        """Train a single model and return results."""
        start = time.time()

        if model_name == "prophet" and date_col:
            return await self._train_prophet(df, date_col, target_col, forecast_periods, start)

        # Sklearn-compatible models
        model = self._get_sklearn_model(model_name)
        if model is None:
            return None

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        from ml_models.base_model import BaseForecaster
        temp = BaseForecaster.__new__(BaseForecaster)
        metrics = temp.evaluate(y_test.values, y_pred)

        # Feature importance
        feature_importance = None
        if hasattr(model, "feature_importances_"):
            fi = dict(zip(X_train.columns, model.feature_importances_))
            feature_importance = dict(sorted(fi.items(), key=lambda x: -x[1])[:10])

        # Future forecast (extrapolate using last known X)
        future_preds = []
        forecast_dates = []
        if len(X_test) > 0:
            last_x = X_test.iloc[[-1]]
            for i in range(forecast_periods):
                pred = float(model.predict(last_x)[0])
                future_preds.append(pred)
                if date_col and date_col in df.columns:
                    last_date = pd.to_datetime(df[date_col]).max()
                    forecast_dates.append(str((last_date + pd.Timedelta(days=i+1)).date()))
                else:
                    forecast_dates.append(f"Period+{i+1}")

        # Save model
        model_path = os.path.join(settings.ML_MODELS_DIR, f"{model_name}_{target_col}.joblib")
        joblib.dump(model, model_path)

        return ModelResult(
            model_name=model_name,
            predictions=future_preds,
            forecast_dates=forecast_dates,
            metrics=metrics,
            feature_importance=feature_importance,
            training_time=time.time() - start,
            lower_bound=[p * 0.9 for p in future_preds],
            upper_bound=[p * 1.1 for p in future_preds],
        )

    async def _train_prophet(
        self, df, date_col, target_col, forecast_periods, start
    ) -> Optional[ModelResult]:
        """Train Facebook Prophet model."""
        try:
            from prophet import Prophet
            prophet_df = df[[date_col, target_col]].rename(
                columns={date_col: "ds", target_col: "y"}
            )
            prophet_df["ds"] = pd.to_datetime(prophet_df["ds"], errors="coerce")
            prophet_df = prophet_df.dropna()

            split_idx = int(len(prophet_df) * 0.8)
            train = prophet_df.iloc[:split_idx]
            test = prophet_df.iloc[split_idx:]

            model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
            model.fit(train)

            # Evaluate
            if len(test) > 0:
                future_eval = model.make_future_dataframe(periods=len(test))
                forecast_eval = model.predict(future_eval)
                y_pred = forecast_eval["yhat"].values[-len(test):]
                temp = object.__new__(object)

                from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
                y_true = test["y"].values
                mae = float(mean_absolute_error(y_true, y_pred))
                rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
                r2 = float(r2_score(y_true, y_pred))
                metrics = {"mae": mae, "rmse": rmse, "r2": r2, "mape": 0.0}
            else:
                metrics = {"mae": 0, "rmse": 0, "r2": 0, "mape": 0}

            # Future forecast
            future = model.make_future_dataframe(periods=forecast_periods)
            forecast = model.predict(future)
            future_forecast = forecast.tail(forecast_periods)

            preds = future_forecast["yhat"].tolist()
            dates = [str(d.date()) for d in future_forecast["ds"]]
            lower = future_forecast["yhat_lower"].tolist()
            upper = future_forecast["yhat_upper"].tolist()

            return ModelResult(
                model_name="prophet",
                predictions=preds,
                forecast_dates=dates,
                metrics=metrics,
                feature_importance=None,
                training_time=time.time() - start,
                lower_bound=lower,
                upper_bound=upper,
            )
        except Exception as e:
            logger.error(f"Prophet training error: {e}")
            return None

    def _get_sklearn_model(self, model_name: str):
        """Get sklearn-compatible model by name."""
        from sklearn.linear_model import LinearRegression, Ridge
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

        models = {
            "linear_regression": LinearRegression(),
            "ridge": Ridge(alpha=1.0),
            "random_forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        }

        if model_name == "xgboost":
            try:
                import xgboost as xgb
                return xgb.XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
            except ImportError:
                logger.warning("XGBoost not available, falling back to GBR")
                return GradientBoostingRegressor(n_estimators=100, random_state=42)

        return models.get(model_name)


_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
