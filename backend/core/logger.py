# backend/core/logger.py
import sys
from loguru import logger
from backend.core.config import settings
import os

os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

# Remove default handler
logger.remove()

# Console handler — rich colored output
logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    level=settings.LOG_LEVEL,
    colorize=True,
)

# File handler — JSON structured logs
logger.add(
    settings.LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level=settings.LOG_LEVEL,
    rotation="50 MB",
    retention="30 days",
    compression="zip",
    serialize=False,
)

__all__ = ["logger"]
