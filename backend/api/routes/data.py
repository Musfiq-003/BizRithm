# backend/api/routes/data.py
"""Data management: upload, list, preview datasets."""
import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.config import settings
from backend.core.logger import logger
from backend.models.user import User
from backend.models.dataset import Dataset
from backend.api.middleware.auth_middleware import get_current_user
from utils.data_processor import load_file, clean_dataframe, get_column_metadata, get_dataframe_summary

router = APIRouter()


async def process_dataset(dataset_id: str, file_path: str, db_url: str):
    """Background task: process and ingest uploaded file."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from backend.core.database import AsyncSessionLocal
    from sqlalchemy import update
    import pandas as pd

    async with AsyncSessionLocal() as session:
        try:
            df = load_file(file_path)
            df = clean_dataframe(df)
            meta = get_column_metadata(df)
            summary = get_dataframe_summary(df)

            # Ingest into PostgreSQL as a table
            table_name = f"ds_{dataset_id.replace('-', '_')[:20]}"

            await session.execute(
                update(Dataset)
                .where(Dataset.id == dataset_id)
                .values(
                    status="ready",
                    row_count=summary["rows"],
                    column_count=summary["columns"],
                    columns_meta=meta,
                    table_name=table_name,
                )
            )
            await session.commit()
            logger.info(f"Dataset {dataset_id} processed: {summary['rows']} rows")
        except Exception as e:
            logger.error(f"Dataset processing error: {e}")
            await session.execute(
                update(Dataset)
                .where(Dataset.id == dataset_id)
                .values(status="error", error_message=str(e))
            )
            await session.commit()


@router.post("/upload", status_code=201)
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a dataset file (CSV, Excel)."""
    # Validate file type
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(400, f"File type .{ext} not supported. Use: {settings.ALLOWED_EXTENSIONS}")

    # Validate size
    file_content = await file.read()
    if len(file_content) > settings.max_upload_size_bytes:
        raise HTTPException(413, f"File too large. Max: {settings.MAX_UPLOAD_SIZE_MB}MB")

    # Save file
    dataset_id = str(uuid.uuid4())
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{dataset_id}.{ext}")

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Create dataset record
    dataset = Dataset(
        id=dataset_id,
        user_id=current_user.id,
        name=name,
        description=description,
        file_path=file_path,
        file_type=ext,
        file_size_bytes=len(file_content),
        status="processing",
    )
    db.add(dataset)
    await db.flush()

    # Background processing
    background_tasks.add_task(process_dataset, dataset_id, file_path, settings.DATABASE_URL)

    logger.info(f"Dataset uploaded: {name} by {current_user.email}")
    return {
        "success": True,
        "dataset_id": dataset_id,
        "name": name,
        "status": "processing",
        "message": "File uploaded. Processing in background.",
    }


@router.get("/list")
async def list_datasets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all datasets for the current user."""
    result = await db.execute(
        select(Dataset)
        .where(Dataset.user_id == current_user.id)
        .order_by(Dataset.created_at.desc())
    )
    datasets = result.scalars().all()
    return {
        "datasets": [
            {
                "id": str(d.id),
                "name": d.name,
                "description": d.description,
                "file_type": d.file_type,
                "file_size_mb": round((d.file_size_bytes or 0) / 1024 / 1024, 2),
                "row_count": d.row_count,
                "column_count": d.column_count,
                "status": d.status,
                "table_name": d.table_name,
                "created_at": str(d.created_at),
            }
            for d in datasets
        ]
    }


@router.get("/{dataset_id}/preview")
async def preview_dataset(
    dataset_id: str,
    rows: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Preview first N rows of a dataset."""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    try:
        import pandas as pd
        df = load_file(dataset.file_path)
        df = clean_dataframe(df)
        from utils.data_processor import df_to_safe_json
        return {
            "dataset_id": dataset_id,
            "name": dataset.name,
            "rows": df_to_safe_json(df, rows),
            "columns": dataset.columns_meta or [],
            "total_rows": len(df),
        }
    except Exception as e:
        raise HTTPException(500, f"Preview failed: {str(e)}")


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a dataset."""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    # Remove file
    if dataset.file_path and os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)

    await db.delete(dataset)
    return {"success": True, "message": "Dataset deleted"}
