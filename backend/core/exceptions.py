# backend/core/exceptions.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.core.logger import logger


class BizRithmException(Exception):
    """Base exception for BizRithm."""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(message)


class DatasetNotFoundError(BizRithmException):
    def __init__(self, dataset_id: str):
        super().__init__(f"Dataset {dataset_id} not found", 404)


class InvalidFileTypeError(BizRithmException):
    def __init__(self, ext: str):
        super().__init__(f"File type '.{ext}' is not supported", 400)


class MLModelError(BizRithmException):
    def __init__(self, msg: str):
        super().__init__(f"ML model error: {msg}", 500)


class SQLInjectionError(BizRithmException):
    def __init__(self):
        super().__init__("Potentially unsafe SQL detected", 400)


class AgentError(BizRithmException):
    def __init__(self, agent: str, msg: str):
        super().__init__(f"Agent '{agent}' failed: {msg}", 500)


# ── FastAPI Exception Handlers ──────────────────────────────

async def bizrithm_exception_handler(request: Request, exc: BizRithmException):
    logger.warning(f"BizRithm exception [{exc.code}]: {exc.message}")
    return JSONResponse(
        status_code=exc.code,
        content={"success": False, "error": exc.message, "code": exc.code}
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} | {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": str(exc.detail), "code": exc.status_code}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed",
            "details": [{"field": e["loc"], "msg": e["msg"]} for e in errors]
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )
