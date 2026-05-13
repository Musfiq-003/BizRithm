# backend/main.py
"""
BizRithm FastAPI Application Entry Point
"""
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.config import settings
from backend.core.database import init_db, close_db
from backend.core.logger import logger
from backend.core.exceptions import (
    BizRithmException,
    bizrithm_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from backend.api.routes import auth, data, chat, sql_explorer, ml, insights, reports

# ── Directories Setup ────────────────────────────────────────
for directory in [
    settings.UPLOAD_DIR,
    settings.REPORTS_DIR,
    settings.CHARTS_DIR,
    settings.ML_MODELS_DIR,
    "./logs",
]:
    os.makedirs(directory, exist_ok=True)


# ── Lifespan ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    logger.info("✅ All services initialized")
    yield
    await close_db()
    logger.info("🔌 BizRithm shutdown complete")


# ── Application ──────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Business Consultant Agent Platform",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── Middleware ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    response.headers["X-BizRithm-Version"] = settings.APP_VERSION
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.debug(f"← {response.status_code} {request.url.path}")
    return response


# ── Exception Handlers ───────────────────────────────────────
app.add_exception_handler(BizRithmException, bizrithm_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ── Routers ──────────────────────────────────────────────────
app.include_router(auth.router,         prefix="/api/auth",     tags=["Authentication"])
app.include_router(data.router,         prefix="/api/data",     tags=["Data Management"])
app.include_router(chat.router,         prefix="/api/chat",     tags=["AI Chat"])
app.include_router(sql_explorer.router, prefix="/api/sql",      tags=["SQL Explorer"])
app.include_router(ml.router,           prefix="/api/ml",       tags=["ML Forecasting"])
app.include_router(insights.router,     prefix="/api/insights", tags=["Business Insights"])
app.include_router(reports.router,      prefix="/api/reports",  tags=["PDF Reports"])


# ── Core Endpoints ───────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "message": "AI Business Consultant Agent — Ready"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@app.get("/api/status", tags=["Status"])
async def api_status():
    return {
        "api_version": "v1",
        "endpoints": {
            "auth": "/api/auth",
            "data": "/api/data",
            "chat": "/api/chat",
            "sql": "/api/sql",
            "ml": "/api/ml",
            "insights": "/api/insights",
            "reports": "/api/reports",
        },
        "features": {
            "ai_chat": True,
            "nl2sql": True,
            "ml_forecasting": True,
            "pdf_reports": True,
            "multi_agent": True,
            "lstm": settings.ENABLE_LSTM,
        }
    }
