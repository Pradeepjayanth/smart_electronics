"""
Analytics Routes
================

REST endpoints exposing the Analytics Engine aggregations and prognostic trends
to the frontend dashboard.
"""

from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.database.mongodb import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics Engine"])


@router.get(
    "/averages",
    summary="Get system-wide averages",
    description="Retrieve average temperature, humidity, voltage, current, and health scores across active devices.",
)
async def get_averages(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_averages()


@router.get(
    "/risk-distribution",
    summary="Get device risk distribution",
    description="Get counts of devices currently in Low, Medium, High, and Critical risk tiers.",
)
async def get_risk_distribution(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_risk_distribution()


@router.get(
    "/most-failed-devices",
    summary="Get most failed devices",
    description="Get a list of devices with the lowest health scores or highest failure risk.",
)
async def get_most_failed_devices(
    limit: int = Query(default=5, ge=1, le=50, description="Max devices to return"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_most_failed_devices(limit=limit)


@router.get(
    "/common-causes",
    summary="Get most common failure causes",
    description="Retrieve the top identified root causes across historical predictions.",
)
async def get_common_causes(
    limit: int = Query(default=5, ge=1, le=50, description="Max causes to return"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_most_common_failure_causes(limit=limit)


@router.get(
    "/trends",
    summary="Get failure and prediction trends",
    description="Retrieve daily average failure probabilities and prediction counts over a given timeframe.",
)
async def get_trends(
    days: int = Query(default=7, ge=1, le=365, description="Number of days to analyze"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_trends(days=days)
