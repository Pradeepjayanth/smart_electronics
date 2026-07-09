"""
Global Error Handler Middleware
================================

Catches all unhandled exceptions and returns consistent JSON error responses.
In production, stack traces are suppressed to prevent information leakage.
In development, full error details are included for debugging.

HTTP status codes used:
    400 — Bad Request (validation errors)
    401 — Unauthorized (missing/invalid auth)
    403 — Forbidden (insufficient permissions)
    404 — Not Found
    500 — Internal Server Error (unhandled exceptions)
"""

import traceback

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.utils.logger import logger


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers on the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors (422 → 400).

        Converts FastAPI's default 422 Unprocessable Entity into a
        400 Bad Request with human-readable error details.
        """
        errors = []
        for error in exc.errors():
            field = " → ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })

        logger.warning(f"Validation error on {request.url}: {errors}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Validation error",
                "errors": errors,
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(
        request: Request, exc: ValueError
    ) -> JSONResponse:
        """Handle ValueError as 400 Bad Request."""
        logger.warning(f"ValueError on {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all handler for unhandled exceptions.

        Returns a generic 500 response. In development mode, includes
        the error details for debugging. In production, suppresses
        the stack trace for security.
        """
        settings = get_settings()

        logger.error(
            f"Unhandled exception on {request.method} {request.url}: "
            f"{type(exc).__name__}: {exc}"
        )
        logger.error(traceback.format_exc())

        detail = (
            f"{type(exc).__name__}: {exc}"
            if settings.DEBUG
            else "An internal server error occurred."
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error",
                "detail": detail,
            },
        )
