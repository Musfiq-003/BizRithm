# analytics/recommendation_engine.py
"""Rule-based + ML recommendation engine for business strategy."""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class RecommendationEngine:
    """Generate actionable business recommendations from data patterns."""

    def generate_recommendations(
        self,
        kpis: Dict[str, Any],
        anomalies: List[Dict],
        trends: Dict[str, Any],
        context: str = "general"
    ) -> List[Dict[str, Any]]:
        """Generate prioritized business recommendations."""
        recommendations = []

        # Revenue-based recommendations
        recommendations.extend(self._revenue_recommendations(kpis))

        # Trend-based recommendations
        recommendations.extend(self._trend_recommendations(trends))

        # Anomaly-based recommendations
        recommendations.extend(self._anomaly_recommendations(anomalies))

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))

        return recommendations[:10]  # Top 10 recommendations

    def _revenue_recommendations(self, kpis: Dict) -> List[Dict]:
        recs = []
        mom = kpis.get("mom_change", {})

        if isinstance(mom, dict):
            pct = mom.get("pct", 0)
            if pct < -10:
                recs.append({
                    "title": "Revenue Decline Alert",
                    "description": f"Revenue dropped {abs(pct):.1f}% month-over-month. Review pricing strategy and identify lost customers.",
                    "action": "Analyze customer churn and competitor pricing immediately",
                    "impact": "High",
                    "priority": "critical",
                    "category": "revenue",
                    "icon": "🚨",
                })
            elif pct > 20:
                recs.append({
                    "title": "Scale Winning Strategy",
                    "description": f"Revenue grew {pct:.1f}% this month. Identify what's working and scale it.",
                    "action": "Double down on top-performing channels and products",
                    "impact": "High",
                    "priority": "high",
                    "category": "growth",
                    "icon": "🚀",
                })

        repeat_rate = kpis.get("repeat_rate", 0)
        if isinstance(repeat_rate, (int, float)) and repeat_rate < 20:
            recs.append({
                "title": "Improve Customer Retention",
                "description": f"Only {repeat_rate:.1f}% of customers make repeat purchases. Implement a loyalty program.",
                "action": "Launch email re-engagement campaign and loyalty rewards",
                "impact": "Medium",
                "priority": "high",
                "category": "retention",
                "icon": "💎",
            })

        return recs

    def _trend_recommendations(self, trends: Dict) -> List[Dict]:
        recs = []
        trend_info = trends.get("trend", {})

        if trend_info.get("direction") == "down" and trend_info.get("is_significant"):
            recs.append({
                "title": "Declining Trend Detected",
                "description": "A statistically significant downward trend has been identified in your key metric.",
                "action": "Conduct root cause analysis and implement corrective measures within 30 days",
                "impact": "High",
                "priority": "critical",
                "category": "trend",
                "icon": "📉",
            })

        peak_month = trends.get("peak_month")
        if peak_month:
            recs.append({
                "title": f"Prepare for {peak_month} Peak Season",
                "description": f"{peak_month} is historically your strongest month. Maximize inventory and marketing.",
                "action": "Increase stock levels and launch targeted campaigns 6 weeks before peak",
                "impact": "High",
                "priority": "medium",
                "category": "planning",
                "icon": "📅",
            })

        return recs

    def _anomaly_recommendations(self, anomalies: List[Dict]) -> List[Dict]:
        recs = []
        high_anomalies = [a for a in anomalies if a.get("severity") == "high"]

        if high_anomalies:
            recs.append({
                "title": f"Investigate {len(high_anomalies)} Data Anomalies",
                "description": f"Detected {len(high_anomalies)} high-severity anomalies that may indicate data quality issues or unusual events.",
                "action": "Review anomalous records and verify data accuracy",
                "impact": "Medium",
                "priority": "high",
                "category": "data_quality",
                "icon": "🔍",
            })

        return recs

    def generate_product_recommendations(self, product_data: List[Dict]) -> List[Dict]:
        """Generate product-specific recommendations."""
        recs = []
        if not product_data:
            return recs

        # Find underperforming products (bottom 20% by revenue)
        revenues = [p.get("revenue", 0) for p in product_data]
        threshold = np.percentile(revenues, 20)

        underperformers = [p for p in product_data if p.get("revenue", 0) <= threshold]
        if underperformers:
            recs.append({
                "title": "Optimize Low-Performing Products",
                "description": f"{len(underperformers)} products are in the bottom 20% of revenue.",
                "action": "Consider discontinuing or re-positioning these products",
                "impact": "Medium",
                "priority": "medium",
                "category": "product",
                "icon": "📦",
            })

        return recs


_engine: Optional[RecommendationEngine] = None


def get_recommendation_engine() -> RecommendationEngine:
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine
