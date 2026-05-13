# backend/api/routes/sql_explorer.py
"""NL-to-SQL Explorer API routes."""
import uuid
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import pandas as pd
import io

from backend.core.database import get_db
from backend.core.logger import logger
from backend.models.user import User
from backend.models.dataset import Dataset
from backend.models.sql_query import SQLQuery
from backend.schemas.sql import NL2SQLRequest, SQLExecuteRequest
from backend.api.middleware.auth_middleware import get_current_user
from agents.sql_agent import get_sql_agent

router = APIRouter()


@router.post("/generate")
async def generate_sql(
    request: NL2SQLRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Convert natural language question to SQL query."""
    agent = get_sql_agent()

    # Get dataset schema
    columns = []
    table_name = request.table_name or "data"
    sample_data = None

    if request.dataset_id:
        result = await db.execute(
            select(Dataset).where(Dataset.id == request.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if dataset:
            columns = dataset.columns_meta or []
            table_name = dataset.table_name or table_name

    # Generate SQL
    start = time.time()
    gen_result = await agent.generate_sql(
        question=request.question,
        table_name=table_name,
        columns=columns,
        sample_data=sample_data,
    )

    if not gen_result["success"]:
        raise HTTPException(400, gen_result.get("error", "SQL generation failed"))

    sql = gen_result["sql"]
    results = None
    row_count = 0
    exec_time = None

    # Execute if requested
    if request.execute:
        exec_result = await agent.execute_query(sql, db, request.limit)
        results = exec_result.get("results", [])
        row_count = exec_result.get("row_count", 0)
        exec_time = exec_result.get("execution_time_ms")

    # Save to history
    query_record = SQLQuery(
        user_id=current_user.id,
        dataset_id=request.dataset_id,
        natural_language=request.question,
        generated_sql=sql,
        execution_time_ms=exec_time,
        row_count=row_count,
        status="success" if gen_result["success"] else "error",
        result_preview=results[:10] if results else None,
    )
    db.add(query_record)

    return {
        "query_id": str(query_record.id) if query_record.id else str(uuid.uuid4()),
        "natural_language": request.question,
        "generated_sql": sql,
        "explanation": gen_result.get("explanation", ""),
        "results": results,
        "row_count": row_count,
        "execution_time_ms": exec_time,
        "chart_suggestion": agent.suggest_chart_type(sql, [c["name"] for c in columns]),
        "status": "success",
    }


@router.post("/execute")
async def execute_sql(
    request: SQLExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute a raw SQL query safely."""
    agent = get_sql_agent()
    result = await agent.execute_query(request.sql, db, request.limit)

    if not result["success"]:
        raise HTTPException(400, result.get("error", "Execution failed"))

    return result


@router.get("/history")
async def get_query_history(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get SQL query history."""
    result = await db.execute(
        select(SQLQuery)
        .where(SQLQuery.user_id == current_user.id)
        .order_by(SQLQuery.created_at.desc())
        .limit(limit)
    )
    queries = result.scalars().all()

    return {
        "queries": [
            {
                "id": str(q.id),
                "natural_language": q.natural_language,
                "generated_sql": q.generated_sql,
                "row_count": q.row_count,
                "execution_time_ms": q.execution_time_ms,
                "status": q.status,
                "is_bookmarked": q.is_bookmarked,
                "created_at": str(q.created_at),
            }
            for q in queries
        ]
    }


@router.get("/export/{query_id}")
async def export_results(
    query_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export query results as CSV."""
    result = await db.execute(
        select(SQLQuery).where(
            SQLQuery.id == query_id,
            SQLQuery.user_id == current_user.id
        )
    )
    query = result.scalar_one_or_none()
    if not query or not query.result_preview:
        raise HTTPException(404, "Query results not found")

    df = pd.DataFrame(query.result_preview)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=query_{query_id[:8]}.csv"},
    )
