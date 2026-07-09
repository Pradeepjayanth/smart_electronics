"""
Audit Log Routes
================

REST endpoints enabling authorized administrators to query system security
and operational audit trails with pagination and status filtering.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_admin_user, get_current_user
from app.database.mongodb import get_db
from app.schemas.audit_log import AuditLogCreateRequest
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Record an audit action",
    description="Manually record a system audit event or security action.",
)
async def create_audit_log(
    request: AuditLogCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AuditService(db)
    return await service.record_action(
        action=request.action,
        actor_id=request.actor_id,
        actor_type=request.actor_type,
        details=request.details,
        ip_address=request.ip_address,
        status=request.status,
    )


@router.get(
    "",
    summary="Get paginated audit logs",
    description="Retrieve system audit logs filtered by actor, action category, or status code.",
)
async def get_audit_logs(
    actor_id: Optional[str] = Query(default=None, description="Filter by User or Device ID"),
    action: Optional[str] = Query(default=None, description="Filter by action name"),
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filter by status (success/failure)"),
    limit: int = Query(default=50, ge=1, le=200, description="Max logs per page"),
    page: int = Query(default=1, ge=1, description="Page number"),
    current_admin: dict = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = AuditService(db)
    return await service.get_logs(
        actor_id=actor_id,
        action=action,
        status=status_filter,
        limit=limit,
        page=page,
    )
