# agents/orchestrator.py
"""Master orchestrator agent that coordinates all sub-agents."""
import uuid
from typing import Dict, Any, Optional
from backend.core.logger import logger
from agents.chat_agent import get_chat_agent
from agents.sql_agent import get_sql_agent


class OrchestratorAgent:
    """
    Master orchestrator that:
    - Receives all user requests
    - Routes to appropriate specialized agents
    - Merges results into unified responses
    - Maintains session context
    """

    def __init__(self):
        self.chat_agent = get_chat_agent()
        self.sql_agent = get_sql_agent()
        logger.info("🤖 Orchestrator Agent initialized")

    async def process(
        self,
        request_type: str,
        payload: Dict[str, Any],
        session_id: Optional[str] = None,
        user_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Route request to appropriate agent."""
        logger.info(f"Orchestrator routing: {request_type}")

        handlers = {
            "chat": self._route_chat,
            "sql": self._route_sql,
            "analytics": self._route_analytics,
            "forecast": self._route_forecast,
            "report": self._route_report,
            "insight": self._route_insight,
        }

        handler = handlers.get(request_type, self._route_chat)
        try:
            return await handler(payload, session_id, user_context)
        except Exception as e:
            logger.error(f"Orchestrator error [{request_type}]: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_type": request_type,
            }

    async def _route_chat(self, payload: Dict, session_id: Optional[str], context: Optional[Dict]) -> Dict:
        return await self.chat_agent.chat(
            message=payload.get("message", ""),
            session_id=session_id,
            dataset_context=payload.get("dataset_context"),
            user_info=context,
        )

    async def _route_sql(self, payload: Dict, session_id: Optional[str], context: Optional[Dict]) -> Dict:
        return {
            "success": True,
            "message": "SQL agent ready",
            "agent": "sql_agent",
        }

    async def _route_analytics(self, payload: Dict, session_id: Optional[str], context: Optional[Dict]) -> Dict:
        return {
            "success": True,
            "message": "Analytics agent ready",
            "agent": "analytics_agent",
        }

    async def _route_forecast(self, payload: Dict, session_id: Optional[str], context: Optional[Dict]) -> Dict:
        return {
            "success": True,
            "message": "Forecast agent ready",
            "agent": "forecast_agent",
        }

    async def _route_report(self, payload: Dict, session_id: Optional[str], context: Optional[Dict]) -> Dict:
        return {
            "success": True,
            "message": "Report agent ready",
            "agent": "report_agent",
        }

    async def _route_insight(self, payload: Dict, session_id: Optional[str], context: Optional[Dict]) -> Dict:
        return {
            "success": True,
            "message": "Insight agent ready",
            "agent": "analytics_agent",
        }


_orchestrator: Optional[OrchestratorAgent] = None


def get_orchestrator() -> OrchestratorAgent:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator
