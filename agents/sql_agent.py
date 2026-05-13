# agents/sql_agent.py
"""NL-to-SQL Agent using Gemini API + LangChain."""
import time
import uuid
import pandas as pd
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.logger import logger
from utils.sql_sanitizer import sanitize_sql, add_limit_clause

genai.configure(api_key=settings.GEMINI_API_KEY)


class SQLAgent:
    """Converts natural language to SQL and executes it safely."""

    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.history: List[Dict] = []

    def build_schema_context(self, schema_info: Dict[str, Any]) -> str:
        """Build a schema context string for the LLM prompt."""
        if not schema_info:
            return "No schema available."

        lines = ["Database Schema:\n"]
        for table, cols in schema_info.items():
            lines.append(f"Table: {table}")
            for col in cols:
                lines.append(f"  - {col['name']} ({col['dtype']})")
            lines.append("")

        return "\n".join(lines)

    async def generate_sql(
        self,
        question: str,
        table_name: str,
        columns: List[Dict[str, Any]],
        sample_data: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Generate a SQL query from natural language."""
        schema_str = f"Table: {table_name}\nColumns:\n"
        for col in columns:
            schema_str += f"  - {col['name']} ({col['dtype']})\n"

        sample_str = ""
        if sample_data:
            sample_str = f"\nSample rows (first 3):\n"
            for row in sample_data[:3]:
                sample_str += f"  {row}\n"

        prompt = f"""You are an expert PostgreSQL query generator.

{schema_str}
{sample_str}

User question: "{question}"

Rules:
1. Generate ONLY a SELECT query — no INSERT, UPDATE, DELETE, or DDL
2. Use proper PostgreSQL syntax
3. Use column names exactly as defined in the schema
4. Add appropriate GROUP BY, ORDER BY, LIMIT clauses
5. Return ONLY the raw SQL query, nothing else — no markdown, no explanation

SQL Query:"""

        try:
            response = self.model.generate_content(prompt)
            raw_sql = response.text.strip().strip("```sql").strip("```").strip()

            # Clean up any markdown artifacts
            if raw_sql.upper().startswith("SQL"):
                raw_sql = raw_sql[3:].strip()

            is_safe, result = sanitize_sql(raw_sql)
            if not is_safe:
                return {"success": False, "error": result, "sql": raw_sql}

            sql_with_limit = add_limit_clause(result, limit=1000)

            # Generate explanation
            explanation = await self._explain_sql(question, sql_with_limit)

            return {
                "success": True,
                "sql": sql_with_limit,
                "explanation": explanation,
            }

        except Exception as e:
            logger.error(f"SQL generation error: {e}")
            return {"success": False, "error": str(e), "sql": ""}

    async def _explain_sql(self, question: str, sql: str) -> str:
        """Generate a plain-English explanation of the SQL query."""
        prompt = f"""Explain this SQL query in 1-2 simple sentences for a non-technical user:

Question: {question}
SQL: {sql}

Explanation (no technical jargon):"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "This query retrieves the requested business data from the database."

    async def execute_query(
        self,
        sql: str,
        db: AsyncSession,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Execute SQL safely and return results."""
        start_time = time.time()
        try:
            is_safe, clean_sql = sanitize_sql(sql)
            if not is_safe:
                return {"success": False, "error": clean_sql, "results": [], "row_count": 0}

            result = await db.execute(text(clean_sql))
            rows = result.fetchmany(limit)
            columns = list(result.keys())

            results = [dict(zip(columns, row)) for row in rows]
            execution_time = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "results": results,
                "row_count": len(results),
                "columns": columns,
                "execution_time_ms": execution_time,
            }
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return {"success": False, "error": str(e), "results": [], "row_count": 0}

    def suggest_chart_type(self, sql: str, columns: List[str]) -> str:
        """Suggest an appropriate chart type for the query results."""
        sql_upper = sql.upper()
        if "GROUP BY" in sql_upper and "SUM" in sql_upper:
            return "bar"
        elif "ORDER BY" in sql_upper and any(c in sql_upper for c in ["DATE", "MONTH", "YEAR"]):
            return "line"
        elif len(columns) == 2:
            return "bar"
        return "table"


_sql_agent: Optional[SQLAgent] = None


def get_sql_agent() -> SQLAgent:
    global _sql_agent
    if _sql_agent is None:
        _sql_agent = SQLAgent()
    return _sql_agent
