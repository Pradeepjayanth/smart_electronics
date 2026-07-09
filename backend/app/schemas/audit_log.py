"""
Audit Log Schemas
=================

Pydantic schemas for creating and querying audit trail records.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AuditLogCreateRequest(BaseModel):
    """Schema for recording a new audit log entry."""
    action: str = Field(..., description="Action name e.g. user_login, sensor_upload")
    actor_id: str = Field(..., description="User or Device ID")
    actor_type: str = Field(default="user", description="Type of actor: user or device")
    details: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    ip_address: str = Field(default="127.0.0.1", description="Source IP address")
    status: str = Field(default="success", description="Status: success or failure")


class AuditLogResponse(BaseModel):
    """Schema for returning an audit log entry."""
    id: str
    action: str
    actor_id: str
    actor_type: str
    details: Dict[str, Any]
    ip_address: str
    status: str
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Schema for a paginated list of audit logs."""
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
