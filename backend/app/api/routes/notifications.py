"""
Notification Routes
===================

REST endpoints allowing users to retrieve paginated alerts, check unread counts,
and mark alerts as read.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.database.mongodb import get_db
from app.schemas.notification import NotificationCreateRequest
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notification Engine"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Dispatch a new notification",
    description="Create and dispatch an alert via Dashboard and configured multi-channel routes.",
)
async def create_notification(
    request: NotificationCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = NotificationService(db)
    return await service.create_notification(request)


@router.get(
    "",
    summary="Get user notifications",
    description="Retrieve paginated dashboard notifications for the authenticated user.",
)
async def get_my_notifications(
    unread_only: bool = Query(default=False, description="Filter to unread alerts only"),
    limit: int = Query(default=20, ge=1, le=100, description="Max notifications to return"),
    page: int = Query(default=1, ge=1, description="Page number"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = NotificationService(db)
    return await service.get_user_notifications(
        user_id=current_user["_id"], unread_only=unread_only, limit=limit, page=page
    )


@router.patch(
    "/{notification_id}/read",
    summary="Mark notification as read",
    description="Update the status of a specific alert to read.",
)
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = NotificationService(db)
    success = await service.mark_as_read(notification_id=notification_id, user_id=current_user["_id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or already read.",
        )
    return {"status": "success", "message": "Notification marked as read."}
