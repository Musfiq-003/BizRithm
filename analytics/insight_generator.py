# analytics/insight_generator.py
"""AI-powered business insight generator using Gemini API."""
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
from backend.core.config import settings
from backend.core.logger import logger

genai.configure(api_key=settings.GEMINI_API_KEY)


class InsightGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def generate_kpi_insights(self, kpis: Dict[str, Any], context: str = "") -> str:
        """Generate human-readable business insights from KPI data."""
        prompt = f"""You are a senior business analyst. Based on the following KPI data, 
generate 3-5 concise, actionable business insights in professional language.

KPI Data:
{json.dumps(kpis, indent=2, default=str)}

Business Context: {context or "General business analytics"}

Requirements:
- Start each insight with a specific number or percentage
- Be direct and business-focused
- Identify both opportunities and risks
- Keep each insight to 1-2 sentences
- Format as a numbered list

Generate insights:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Insight generation error: {e}")
            return self._fallback_insights(kpis)

    async def generate_anomaly_insight(self, anomalies: List[Dict]) -> str:
        """Generate insight about detected anomalies."""
        if not anomalies:
            return "No significant anomalies detected in the current dataset."

        prompt = f"""As a business analyst, explain these data anomalies in simple business terms:

Anomalies detected:
{json.dumps(anomalies, indent=2, default=str)}

Provide a brief, actionable explanation (2-3 sentences) for each anomaly, 
focusing on potential business impact and recommended actions."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Anomaly insight error: {e}")
            return "Several data anomalies were detected that may require attention."

    async def generate_forecast_insight(self, forecast_data: Dict, metrics: Dict) -> str:
        """Generate insight about ML forecast results."""
        prompt = f"""As a business forecasting expert, analyze these prediction results:

Model Performance:
- Best Model: {forecast_data.get('best_model', 'Unknown')}
- MAE: {metrics.get('mae', 'N/A')}
- RMSE: {metrics.get('rmse', 'N/A')}
- R² Score: {metrics.get('r2', 'N/A')}

Forecast Summary:
{json.dumps(forecast_data.get('summary', {}), default=str)}

Write a 2-3 sentence business-friendly interpretation of what these forecasts mean 
and what actions the business should take based on the predicted trends."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Forecast insight error: {e}")
            return "The forecast model has been trained and predictions are available for review."

    async def generate_chat_response(
        self,
        question: str,
        context_data: Optional[Dict] = None,
        chat_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """Generate AI chat response for business questions."""
        context_str = ""
        if context_data:
            context_str = f"\nBusiness Data Context:\n{json.dumps(context_data, indent=2, default=str)}"

        history_str = ""
        if chat_history:
            history_str = "\nPrevious conversation:\n" + "\n".join([
                f"{msg['role'].upper()}: {msg['content'][:200]}"
                for msg in chat_history[-6:]
            ])

        prompt = f"""You are BizRithm AI, an expert business consultant with deep expertise in 
data analytics, business strategy, and financial analysis.

{context_str}
{history_str}

User Question: {question}

Provide a helpful, data-driven response. If data is available, reference specific numbers.
If the question requires SQL or ML analysis, indicate that and suggest next steps.
Keep your response concise and professional (200-300 words max)."""

        try:
            response = self.model.generate_content(prompt)
            return {
                "response": response.text.strip(),
                "intent": self._detect_intent(question),
                "suggestions": self._generate_suggestions(question),
            }
        except Exception as e:
            logger.error(f"Chat response error: {e}")
            return {
                "response": "I apologize, I encountered an issue processing your request. Please try again.",
                "intent": "error",
                "suggestions": [],
            }

    def _detect_intent(self, question: str) -> str:
        """Detect user intent from question."""
        q = question.lower()
        if any(w in q for w in ["sql", "query", "select", "table", "database"]):
            return "sql"
        elif any(w in q for w in ["predict", "forecast", "future", "next month", "trend"]):
            return "forecast"
        elif any(w in q for w in ["why", "reason", "cause", "explain", "insight"]):
            return "insight"
        elif any(w in q for w in ["recommend", "suggest", "strategy", "should", "improve"]):
            return "recommendation"
        elif any(w in q for w in ["revenue", "sales", "profit", "kpi", "performance"]):
            return "analytics"
        return "general"

    def _generate_suggestions(self, question: str) -> List[str]:
        """Generate follow-up question suggestions."""
        return [
            "What are the top performing products this month?",
            "Show me revenue trends for the last 6 months",
            "Which regions have the highest growth rate?",
            "Predict next month's revenue",
        ]

    def _fallback_insights(self, kpis: Dict) -> str:
        """Generate basic insights without AI when API fails."""
        insights = []
        if "total_revenue" in kpis:
            insights.append(f"1. Total revenue stands at {kpis['total_revenue']:,.2f}.")
        if "mom_change" in kpis:
            change = kpis["mom_change"]
            insights.append(f"2. Month-over-month change: {change.get('label', 'N/A')}.")
        if "total_customers" in kpis:
            insights.append(f"3. Total customers: {kpis['total_customers']:,}.")
        return "\n".join(insights) if insights else "Insights could not be generated at this time."


# Singleton
_insight_generator: Optional[InsightGenerator] = None


def get_insight_generator() -> InsightGenerator:
    global _insight_generator
    if _insight_generator is None:
        _insight_generator = InsightGenerator()
    return _insight_generator
