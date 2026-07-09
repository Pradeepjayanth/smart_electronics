"""
Notification Schemas
=====================

Pydantic schemas for notification and alert endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NotificationCreateRequest(BaseModel):
    """Schema for creating a new notification."""
    user_id: str = Field(..., description="Target user ID")
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    alert_type: str = Field(
        default="info",
        description="Alert type: critical, warning, info, success",
    )
    device_id: str = Field(default="", description="Related device ID")
    priority: str = Field(
        default="medium",
        description="Priority: low, medium, high, urgent",
    )
    action_url: str = Field(default="", description="Frontend action URL")


class NotificationResponse(BaseModel):
    """Schema for notification data in API responses."""
    id: str
    user_id: str
    title: str
    message: str
    alert_type: str
    device_id: str
    priority: str
    action_url: str
    is_read: bool
    is_email_sent: bool
    created_at: datetime
    read_at: Optional[datetime] = None


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
