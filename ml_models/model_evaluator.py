# ml_models/model_evaluator.py
"""Model evaluation and comparison engine."""
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from ml_models.base_model import ModelResult
from backend.core.logger import logger


class ModelEvaluator:
    """Compare multiple models and select the best one."""

    def compare_models(self, results: List[ModelResult]) -> Dict[str, Any]:
        """Compare model results and select best by RMSE."""
        if not results:
            return {}

        # Rank by RMSE (lower is better)
        sorted_results = sorted(results, key=lambda r: r.metrics.get("rmse", float("inf")))
        best = sorted_results[0]

        comparison = []
        for r in results:
            comparison.append({
                "model_name": r.model_name,
                "mae": round(r.metrics.get("mae", 0), 4),
                "rmse": round(r.metrics.get("rmse", 0), 4),
                "r2": round(r.metrics.get("r2", 0), 4),
                "mape": round(r.metrics.get("mape", 0), 2),
                "training_time": round(r.training_time, 2),
                "rank": sorted_results.index(r) + 1,
            })

        return {
            "best_model": best.model_name,
            "best_metrics": best.metrics,
            "comparison": comparison,
            "predictions": best.predictions,
            "forecast_dates": best.forecast_dates,
            "lower_bound": best.lower_bound,
            "upper_bound": best.upper_bound,
            "feature_importance": best.feature_importance,
        }

    def generate_evaluation_report(self, comparison: Dict) -> str:
        """Generate text report of model evaluation."""
        lines = [
            f"🏆 Best Model: {comparison['best_model']}",
            f"📊 Metrics:",
            f"  • MAE: {comparison['best_metrics'].get('mae', 'N/A'):.4f}",
            f"  • RMSE: {comparison['best_metrics'].get('rmse', 'N/A'):.4f}",
            f"  • R² Score: {comparison['best_metrics'].get('r2', 'N/A'):.4f}",
            f"  • MAPE: {comparison['best_metrics'].get('mape', 'N/A'):.2f}%",
            "",
            "📈 Model Rankings:",
        ]
        for m in comparison.get("comparison", []):
            lines.append(
                f"  {m['rank']}. {m['model_name']:20s} | RMSE: {m['rmse']:.4f} | R²: {m['r2']:.4f}"
            )
        return "\n".join(lines)


_evaluator: Optional[ModelEvaluator] = None


def get_evaluator() -> ModelEvaluator:
    global _evaluator
    if _evaluator is None:
        _evaluator = ModelEvaluator()
    return _evaluator
