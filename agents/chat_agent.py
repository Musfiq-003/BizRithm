# agents/chat_agent.py
"""Conversational AI Chat Agent with memory and context routing."""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai

from backend.core.config import settings
from backend.core.logger import logger
from analytics.insight_generator import get_insight_generator
from backend.services.vector_store import get_vector_store

genai.configure(api_key=settings.GEMINI_API_KEY)


class ChatAgent:
    """
    Main conversational agent that:
    1. Understands business questions
    2. Routes to appropriate sub-agents (SQL, ML, Analytics)
    3. Maintains conversation memory
    4. Retrieves persistent long-term knowledge via ChromaDB (RAG)
    """

    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.sessions: Dict[str, List[Dict]] = {}  # In-memory session store
        self.insight_gen = get_insight_generator()
        self.vector_store = get_vector_store()

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """Get existing session or create a new one."""
        if session_id is None or session_id not in self.sessions:
            sid = session_id or str(uuid.uuid4())
            self.sessions[sid] = []
            return sid
        return session_id

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        dataset_context: Optional[Dict] = None,
        user_info: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Process a chat message and return a structured response."""
        sid = self.get_or_create_session(session_id)
        history = self.sessions[sid]

        # Detect intent
        intent = self._classify_intent(message)

        # Add user message to history
        history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat(),
        })

        # Generate response based on intent
        try:
            if intent == "greeting":
                response_data = self._handle_greeting(user_info)
            elif intent in ["sql", "data_query"]:
                response_data = await self._handle_data_query(message, dataset_context, history)
            elif intent == "forecast":
                response_data = await self._handle_forecast_request(message, dataset_context)
            elif intent == "recommendation":
                response_data = await self._handle_recommendation(message, dataset_context, history)
            else:
                response_data = await self._handle_general(message, dataset_context, history)

            # Add assistant response to history
            history.append({
                "role": "assistant",
                "content": response_data["response"],
                "timestamp": datetime.now().isoformat(),
            })

            # Keep history bounded
            if len(history) > 20:
                self.sessions[sid] = history[-20:]

            return {
                "session_id": sid,
                "intent": intent,
                **response_data,
            }

        except Exception as e:
            logger.error(f"Chat agent error: {e}")
            return {
                "session_id": sid,
                "intent": intent,
                "response": "I encountered an issue processing your request. Please try again.",
                "suggestions": self._get_default_suggestions(),
            }

    def _classify_intent(self, message: str) -> str:
        """Classify user intent from message."""
        m = message.lower()

        if any(w in m for w in ["hello", "hi", "hey", "good morning", "help"]):
            return "greeting"
        elif any(w in m for w in ["show", "list", "top", "best", "which", "how many", "count", "sum", "total", "average"]):
            return "sql"
        elif any(w in m for w in ["predict", "forecast", "next", "future", "will", "trend", "projection"]):
            return "forecast"
        elif any(w in m for w in ["recommend", "suggest", "should", "strategy", "improve", "optimize"]):
            return "recommendation"
        elif any(w in m for w in ["why", "reason", "explain", "cause", "anomaly", "unusual"]):
            return "insight"
        elif any(w in m for w in ["revenue", "sales", "profit", "kpi", "performance", "growth"]):
            return "analytics"
        return "general"

    def _handle_greeting(self, user_info: Optional[Dict]) -> Dict:
        name = user_info.get("full_name", "there") if user_info else "there"
        return {
            "response": f"Hello {name}! 👋 I'm BizRithm AI, your intelligent business consultant.\n\nI can help you:\n• 📊 **Analyze** your business data\n• 🔍 **Query** your database in plain English\n• 📈 **Forecast** future revenue and trends\n• 💡 **Generate** business insights and recommendations\n• 🧠 **Recall** long-term document context\n\nWhat would you like to explore today?",
            "suggestions": [
                "What are my top 5 products by revenue?",
                "Show me sales trends for the last 6 months",
                "Predict next month's revenue",
                "Which region has the highest growth?",
            ],
        }

    async def _handle_data_query(
        self,
        message: str,
        context: Optional[Dict],
        history: List[Dict],
    ) -> Dict:
        """Handle data query questions by retrieving vector context and suggesting SQL."""
        
        # 1. Retrieve persistent knowledge via RAG
        similar_docs = self.vector_store.query_similar(message, n_results=2)
        rag_context = ""
        if similar_docs:
            rag_context = "\n[Persistent Business Knowledge Found]:\n" + "\n".join([f"- {doc['document']}" for doc in similar_docs])

        # 2. Add current dataset context
        context_str = ""
        if context:
            context_str = f"\n[Available dataset context]: {context.get('dataset_name', 'uploaded dataset')} with columns: {', '.join(context.get('columns', [])[:10])}"

        prompt = f"""You are BizRithm AI. A user wants data from their business dataset.
        
{rag_context}
{context_str}

User question: "{message}"

Provide a helpful response explaining what data you'd retrieve. If possible, show a conceptual SQL query. If persistent knowledge applies to this query, mention it.
Keep it concise and business-focused (150 words max)."""

        try:
            response = self.model.generate_content(prompt)
            return {
                "response": response.text.strip(),
                "suggestions": [
                    "Download results as CSV",
                    "Visualize this data",
                    "Compare with previous period",
                ],
            }
        except Exception as e:
            return {"response": f"I'd analyze your query: '{message}'. Please use the SQL Explorer for direct data queries.", "suggestions": []}

    async def _handle_forecast_request(self, message: str, context: Optional[Dict]) -> Dict:
        return {
            "response": "📈 **Forecast Analysis**\n\nI can predict future trends using 5 ML models:\n• Linear Regression (baseline)\n• Random Forest (robust)\n• XGBoost (high performance)\n• Prophet (time series)\n• LSTM (deep learning)\n\nHead to the **ML Forecasting** page to configure and run predictions on your dataset. I'll analyze the results and generate business insights for you.",
            "suggestions": [
                "Go to ML Forecasting",
                "What is my revenue growth rate?",
                "Show historical trends",
            ],
        }

    async def _handle_recommendation(self, message: str, context: Optional[Dict], history: List[Dict]) -> Dict:
        result = await self.insight_gen.generate_chat_response(message, context, history)
        result["suggestions"] = [
            "Generate full business report",
            "Show me anomalies in the data",
            "What are top opportunities?",
        ]
        return result

    async def _handle_general(self, message: str, context: Optional[Dict], history: List[Dict]) -> Dict:
        """Handle general conversation with full RAG capability."""
        # 1. Retrieve persistent knowledge via RAG
        similar_docs = self.vector_store.query_similar(message, n_results=3)
        rag_context = ""
        if similar_docs:
            rag_context = "\n[Persistent Business Knowledge (RAG)]:\n" + "\n".join([f"- {doc['document']}" for doc in similar_docs])

        # 2. Add history context
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-6:]])

        prompt = f"""You are BizRithm AI, a highly intelligent and professional enterprise AI consultant.
        
{rag_context}

Recent conversation history:
{history_str}

User: "{message}"

Provide a highly professional, strategic response. If the Persistent Business Knowledge is relevant to the question, USE IT and cite it implicitly. 
Keep your response extremely helpful but concise.
"""
        try:
            response = self.model.generate_content(prompt)
            return {
                "response": response.text.strip(),
                "suggestions": self._get_default_suggestions()
            }
        except Exception as e:
            if similar_docs:
                mock_doc = similar_docs[0]['document']
                return {
                    "response": f"(API Offline) Based on our internal persistent knowledge: {mock_doc}",
                    "suggestions": []
                }
            return {
                "response": "I apologize, but I am having trouble connecting to my reasoning engine right now.",
                "suggestions": []
            }

    def _get_default_suggestions(self) -> List[str]:
        return [
            "What are top 5 products by revenue?",
            "Show sales trends for last 6 months",
            "Predict next month's revenue",
            "Generate business report",
        ]

    def clear_session(self, session_id: str):
        """Clear a chat session."""
        if session_id in self.sessions:
            del self.sessions[session_id]


_chat_agent: Optional[ChatAgent] = None


def get_chat_agent() -> ChatAgent:
    global _chat_agent
    if _chat_agent is None:
        _chat_agent = ChatAgent()
    return _chat_agent
