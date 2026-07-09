"""
Main Application Entry Point
============================

Initializes the FastAPI application, configures middleware (CORS),
sets up global exception handlers, manages the database lifespan,
and includes API routers.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import analytics, audit_logs, auth, devices, notifications, reports, sensor_data, users
from app.config import get_settings
from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.database.redis import close_redis_pool, init_redis_pool
from app.middleware.error_handler import register_error_handlers
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events asynchronously.
    """
    # Startup
    logger.info("Starting up Smart Electronics Prediction Platform...")
    await connect_to_mongo()
    await init_redis_pool()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_redis_pool()
    await close_mongo_connection()


def create_app() -> FastAPI:
    """
    Application factory to create and configure the FastAPI instance.
    """
    settings = get_settings()

    # Initialize FastAPI
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Backend API for Smart Electronics Failure Prediction Platform",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup Global Exception Handlers
    register_error_handlers(app)

    # Include Routers
    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(devices.router, prefix=api_prefix)
    app.include_router(sensor_data.router, prefix=api_prefix)
    app.include_router(analytics.router, prefix=api_prefix)
    app.include_router(reports.router, prefix=api_prefix)
    app.include_router(notifications.router, prefix=api_prefix)
    app.include_router(audit_logs.router, prefix=api_prefix)

    @app.get("/", tags=["Health"])
    async def root():
        """Root endpoint for basic health check."""
        return {
            "message": "Welcome to the Smart Electronics Failure Prediction Platform API",
            "version": settings.APP_VERSION,
            "status": "online"
        }

    return app


app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
