"""
Structured Logging Configuration
==================================

Configures application-wide logging using Loguru.
Supports console output (colorized) and file output (with rotation).
In production, logs are formatted as JSON for log aggregation tools.
"""

import sys
from pathlib import Path

from loguru import logger

from app.config import get_settings


def setup_logging() -> None:
    """
    Configure Loguru logger for the application.

    - Removes default stderr handler.
    - Adds a colorized console handler for development.
    - Adds a rotating file handler for persistence.
    - In production, uses structured JSON format.
    """
    settings = get_settings()

    # Remove default handler to avoid duplicate output
    logger.remove()

    # Console handler — colorized for development readability
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # File handler — rotating logs with retention
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if settings.is_production:
        # JSON format for production log aggregation (ELK, Datadog, etc.)
        logger.add(
            str(log_path),
            level=settings.LOG_LEVEL,
            rotation="50 MB",
            retention="30 days",
            compression="gz",
            serialize=True,  # JSON output
        )
    else:
        # Human-readable format for development
        logger.add(
            str(log_path),
            format=log_format,
            level=settings.LOG_LEVEL,
            rotation="10 MB",
            retention="7 days",
        )

    logger.info(
        f"Logging configured — level={settings.LOG_LEVEL}, "
        f"env={settings.APP_ENV}, file={settings.LOG_FILE}"
    )


# Re-export logger for convenient imports across the app:
#   from app.utils.logger import logger
__all__ = ["logger", "setup_logging"]
