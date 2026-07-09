"""
Notification Document Model
=============================

Defines the structure for documents in the 'notifications' MongoDB collection.
Stores alerts (critical, warning) and dashboard notifications.
"""

from datetime import datetime, timezone


def create_notification_document(
    user_id: str,
    title: str,
    message: str,
    alert_type: str = "info",
    device_id: str = "",
    priority: str = "medium",
    action_url: str = "",
) -> dict:
    """
    Create a new notification document for MongoDB insertion.

    Args:
        user_id: The user this notification is for.
        title: Short notification title.
        message: Detailed notification message.
        alert_type: Type of alert (critical, warning, info, success).
        device_id: Related device ID (if applicable).
        priority: Priority level (low, medium, high, urgent).
        action_url: URL for the user to take action (frontend route).

    Returns:
        A dict representing the notification document.
    """
    return {
        "user_id": user_id,
        "title": title,
        "message": message,
        "alert_type": alert_type,
        "device_id": device_id,
        "priority": priority,
        "action_url": action_url,
        "is_read": False,
        "is_email_sent": False,  # Future email support placeholder
        "created_at": datetime.now(timezone.utc),
        "read_at": None,
    }
