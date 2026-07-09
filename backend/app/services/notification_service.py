"""
Notification Service
====================

Service managing multi-channel alert dispatch (Dashboard, Email, SMS, WhatsApp, Push)
prioritized across Critical, Warning, and Info tiers.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.notification import create_notification_document
from app.schemas.notification import NotificationCreateRequest
from app.utils.logger import logger


class NotificationService:
    """Manages creation, dispatch, and persistence of user alerts."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.notifications
        self.users = db.users

    async def create_notification(self, request: NotificationCreateRequest) -> Dict[str, Any]:
        """
        Create a new notification, persist it for the dashboard, and dispatch via
        appropriate secondary channels based on priority and user preferences.
        """
        # Create MongoDB document representation
        doc = create_notification_document(
            user_id=request.user_id,
            title=request.title,
            message=request.message,
            alert_type=request.alert_type,
            device_id=request.device_id,
            priority=request.priority,
            action_url=request.action_url
        )

        # Multi-channel dispatch tracking flags
        doc["is_sms_sent"] = False
        doc["is_whatsapp_sent"] = False
        doc["is_push_sent"] = False

        # Dispatch across secondary channels depending on priority level
        priority = request.priority.lower()
        user = await self._get_user(request.user_id)

        if user:
            # Info / Warning / Critical -> Email check
            if priority in ("info", "medium", "warning", "high", "critical", "urgent"):
                doc["is_email_sent"] = await self.dispatch_email(user, request.title, request.message, priority)

            # Warning / Critical -> Push notifications & WhatsApp check
            if priority in ("warning", "high", "critical", "urgent"):
                doc["is_push_sent"] = await self.dispatch_push(user, request.title, request.message, priority)
                doc["is_whatsapp_sent"] = await self.dispatch_whatsapp(user, request.message, priority)

            # Critical only -> SMS emergency dispatch check
            if priority in ("critical", "urgent"):
                doc["is_sms_sent"] = await self.dispatch_sms(user, request.message, priority)

        # Persist notification document
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id

        logger.info(
            f"Notification dispatched: user={request.user_id}, "
            f"priority={priority}, channels=[DB:True, Email:{doc['is_email_sent']}, "
            f"SMS:{doc['is_sms_sent']}, WhatsApp:{doc['is_whatsapp_sent']}, Push:{doc['is_push_sent']}]"
        )

        return self._format_notification(doc)

    async def get_user_notifications(
        self, user_id: str, unread_only: bool = False, limit: int = 50, page: int = 1
    ) -> Dict[str, Any]:
        """Retrieve paginated notifications for a specific user."""
        query: Dict[str, Any] = {"user_id": user_id}
        if unread_only:
            query["is_read"] = False

        total = await self.collection.count_documents(query)
        unread_count = await self.collection.count_documents({"user_id": user_id, "is_read": False})
        skip = (page - 1) * limit

        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        notifications = [self._format_notification(doc) async for doc in cursor]

        return {
            "notifications": notifications,
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "page_size": limit
        }

    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a specific notification as read by the user."""
        try:
            query_id = ObjectId(notification_id) if ObjectId.is_valid(notification_id) else notification_id
        except Exception:
            query_id = notification_id

        result = await self.collection.update_one(
            {"_id": query_id, "user_id": user_id},
            {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0

    async def _get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch user document to obtain contact info."""
        try:
            if ObjectId.is_valid(user_id):
                return await self.users.find_one({"_id": ObjectId(user_id)})
            return await self.users.find_one({"_id": user_id})
        except Exception:
            return None

    # --- Multi-Channel Dispatch Placeholders ---

    async def dispatch_email(self, user: Dict[str, Any], title: str, message: str, priority: str) -> bool:
        """Placeholder for email dispatch (SendGrid / AWS SES)."""
        logger.debug(f"[EMAIL DISPATCH] To: {user.get('email')} | Priority: {priority} | Title: {title}")
        return True

    async def dispatch_sms(self, user: Dict[str, Any], message: str, priority: str) -> bool:
        """Placeholder for SMS dispatch (Twilio / AWS SNS)."""
        phone = user.get("phone", "N/A")
        logger.warning(f"[SMS DISPATCH] To: {phone} | Priority: {priority} | Msg: {message[:50]}...")
        return True

    async def dispatch_whatsapp(self, user: Dict[str, Any], message: str, priority: str) -> bool:
        """Placeholder for WhatsApp dispatch (Twilio / Meta Graph API)."""
        phone = user.get("phone", "N/A")
        logger.info(f"[WHATSAPP DISPATCH] To: {phone} | Priority: {priority} | Msg: {message[:50]}...")
        return True

    async def dispatch_push(self, user: Dict[str, Any], title: str, message: str, priority: str) -> bool:
        """Placeholder for Mobile Push Notifications (Firebase Cloud Messaging - FCM)."""
        logger.debug(f"[PUSH DISPATCH] User: {str(user.get('_id'))} | Title: {title}")
        return True

    @staticmethod
    def _format_notification(doc: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "title": doc["title"],
            "message": doc["message"],
            "alert_type": doc.get("alert_type", "info"),
            "device_id": doc.get("device_id", ""),
            "priority": doc.get("priority", "medium"),
            "action_url": doc.get("action_url", ""),
            "is_read": doc.get("is_read", False),
            "is_email_sent": doc.get("is_email_sent", False),
            "created_at": doc["created_at"],
            "read_at": doc.get("read_at")
        }
