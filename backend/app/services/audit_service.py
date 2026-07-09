"""
Audit Service
=============

Service responsible for recording and querying system audit logs in MongoDB.
"""

from typing import Any, Dict, List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.audit_log import create_audit_log_document
from app.utils.logger import logger


class AuditService:
    """Manages recording and filtering of security and operational audit trails."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.audit_logs

    async def record_action(
        self,
        action: str,
        actor_id: str,
        actor_type: str = "user",
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "127.0.0.1",
        status: str = "success",
    ) -> Dict[str, Any]:
        """
        Record an audit log entry.

        Args:
            action: 'user_login', 'device_registration', 'prediction_request', etc.
            actor_id: ID of the user or device.
            actor_type: 'user' or 'device'.
            details: Additional dictionary context.
            ip_address: Source request IP.
            status: 'success' or 'failure'.

        Returns:
            The recorded audit log document.
        """
        doc = create_audit_log_document(
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            details=details,
            ip_address=ip_address,
            status=status,
        )

        try:
            result = await self.collection.insert_one(doc)
            doc["_id"] = result.inserted_id
            logger.debug(f"[AUDIT RECORDED] {action} by {actor_type}:{actor_id} ({status})")
        except Exception as e:
            logger.error(f"Failed to insert audit log entry into MongoDB: {e}")

        return self._format_audit_log(doc)

    async def get_logs(
        self,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Query paginated audit trails with optional filtering."""
        query: Dict[str, Any] = {}
        if actor_id:
            query["actor_id"] = actor_id
        if action:
            query["action"] = action
        if status:
            query["status"] = status

        total = await self.collection.count_documents(query)
        skip = (page - 1) * limit

        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        logs = [self._format_audit_log(doc) async for doc in cursor]

        return {
            "logs": logs,
            "total": total,
            "page": page,
            "page_size": limit,
        }

    @staticmethod
    def _format_audit_log(doc: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(doc.get("_id", "")),
            "action": doc.get("action", ""),
            "actor_id": doc.get("actor_id", ""),
            "actor_type": doc.get("actor_type", "user"),
            "details": doc.get("details", {}),
            "ip_address": doc.get("ip_address", "127.0.0.1"),
            "status": doc.get("status", "success"),
            "created_at": doc.get("created_at"),
        }
