# backend/api/routes/reports.py
"""PDF Report generation API routes."""
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.config import settings
from backend.models.user import User
from backend.models.dataset import Dataset
from backend.models.report import Report
from backend.api.middleware.auth_middleware import get_current_user
from backend.core.logger import logger

router = APIRouter()


async def generate_report_task(report_id: str, dataset_file: str, config: dict):
    """Background task to generate PDF report."""
    from backend.core.database import AsyncSessionLocal
    from sqlalchemy import update
    from reports.pdf_generator import PDFReportGenerator
    from utils.data_processor import load_file, clean_dataframe

    async with AsyncSessionLocal() as session:
        try:
            df = load_file(dataset_file)
            df = clean_dataframe(df)

            generator = PDFReportGenerator()
            output_path = os.path.join(settings.REPORTS_DIR, f"{report_id}.pdf")
            os.makedirs(settings.REPORTS_DIR, exist_ok=True)

            await generator.generate(df, output_path, config)

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            await session.execute(
                update(Report)
                .where(Report.id == report_id)
                .values(status="completed", file_path=output_path, file_size_bytes=file_size)
            )
            await session.commit()
            logger.info(f"Report {report_id} generated successfully")

        except Exception as e:
            logger.error(f"Report generation error: {e}")
            await session.execute(
                update(Report).where(Report.id == report_id).values(status="error")
            )
            await session.commit()


@router.post("/generate")
async def generate_report(
    dataset_id: str,
    title: str = "Business Analytics Report",
    report_type: str = "comprehensive",
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a PDF report for a dataset."""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    report_id = str(uuid.uuid4())
    report = Report(
        id=report_id,
        user_id=current_user.id,
        dataset_id=dataset_id,
        title=title,
        report_type=report_type,
        status="generating",
        config={"report_type": report_type, "title": title},
    )
    db.add(report)
    await db.flush()

    config = {
        "title": title,
        "report_type": report_type,
        "dataset_name": dataset.name,
        "user_name": current_user.full_name or current_user.username,
        "company": current_user.company_name or "BizRithm",
    }

    if background_tasks:
        background_tasks.add_task(generate_report_task, report_id, dataset.file_path, config)

    return {
        "report_id": report_id,
        "title": title,
        "status": "generating",
        "message": "Report is being generated. Check status shortly.",
    }


@router.get("/{report_id}/status")
async def get_report_status(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check report generation status."""
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, "Report not found")

    return {
        "report_id": report_id,
        "title": report.title,
        "status": report.status,
        "created_at": str(report.created_at),
    }


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download a generated PDF report."""
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, "Report not found")
    if report.status != "completed":
        raise HTTPException(400, f"Report not ready (status: {report.status})")
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(404, "Report file not found")

    return FileResponse(
        path=report.file_path,
        media_type="application/pdf",
        filename=f"{report.title.replace(' ', '_')}.pdf",
    )


@router.get("/list")
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all reports for the current user."""
    result = await db.execute(
        select(Report)
        .where(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
        .limit(20)
    )
    reports = result.scalars().all()

    return {
        "reports": [
            {
                "id": str(r.id),
                "title": r.title,
                "report_type": r.report_type,
                "status": r.status,
                "created_at": str(r.created_at),
            }
            for r in reports
        ]
    }
