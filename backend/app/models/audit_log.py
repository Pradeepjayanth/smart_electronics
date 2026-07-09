"""
Audit Log Document Model
========================

Defines the document structure for the 'audit_logs' MongoDB collection.
Tracks sensitive system actions, logins, sensor uploads, and configuration changes.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional


def create_audit_log_document(
    action: str,
    actor_id: str,
    actor_type: str = "user",
    details: Optional[Dict[str, Any]] = None,
    ip_address: str = "127.0.0.1",
    status: str = "success",
) -> Dict[str, Any]:
    """
    Create a new audit log document for MongoDB insertion.

    Args:
        action: Type of action ('user_login', 'device_registration', 'prediction_request',
                'sensor_upload', 'config_change', 'password_change').
        actor_id: ID of the user or device performing the action.
        actor_type: 'user' or 'device'.
        details: Additional contextual metadata dictionary.
        ip_address: Source IP address of the request.
        status: Action result ('success' or 'failure').

    Returns:
        Dict representing the audit log document.
    """
    return {
        "action": action,
        "actor_id": actor_id,
        "actor_type": actor_type,
        "details": details or {},
        "ip_address": ip_address,
        "status": status,
        "created_at": datetime.now(timezone.utc),
    }
