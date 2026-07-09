"""
Device Routes
==============

Endpoints for device management — CRUD, assignment, and search.

Routes:
    POST   /devices              — Register a new device
    GET    /devices              — List all devices
    GET    /devices/search       — Search devices
    GET    /devices/{device_id}  — Get device details
    PUT    /devices/{device_id}  — Update device
    DELETE /devices/{device_id}  — Delete device (admin)
    PUT    /devices/{device_id}/assign — Assign device (admin/engineer)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user, require_roles
from app.database.mongodb import get_db
from app.schemas.device import (
    DeviceAssignRequest,
    DeviceCreateRequest,
    DeviceResponse,
    DeviceUpdateRequest,
)
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new device",
)
async def register_device(
    request: DeviceCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Register a new electronic device in the system."""
    service = DeviceService(db)
    try:
        return await service.register_device(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "",
    summary="List all devices",
)
async def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List all devices with pagination."""
    service = DeviceService(db)
    return await service.get_all_devices(page=page, page_size=page_size)


@router.get(
    "/search",
    summary="Search devices",
)
async def search_devices(
    query: str | None = Query(None, description="Search by name or device_id"),
    device_type: str | None = Query(None),
    device_status: str | None = Query(None, alias="status"),
    location: str | None = Query(None),
    assigned_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Search and filter devices with pagination."""
    service = DeviceService(db)
    return await service.search_devices(
        query=query,
        device_type=device_type,
        status=device_status,
        location=location,
        assigned_to=assigned_to,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Get device details",
)
async def get_device(
    device_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get detailed information about a specific device."""
    service = DeviceService(db)
    try:
        return await service.get_device(device_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Update device",
)
async def update_device(
    device_id: str,
    request: DeviceUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update details of an existing device."""
    service = DeviceService(db)
    try:
        return await service.update_device(device_id, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/{device_id}",
    summary="Delete device",
    dependencies=[Depends(require_roles("admin"))],
)
async def delete_device(
    device_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Delete a device. Admin only."""
    service = DeviceService(db)
    try:
        return await service.delete_device(device_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.put(
    "/{device_id}/assign",
    response_model=DeviceResponse,
    summary="Assign device to user",
    dependencies=[Depends(require_roles("admin", "engineer"))],
)
async def assign_device(
    device_id: str,
    request: DeviceAssignRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Assign a device to a specific user. Admin and Engineer only."""
    service = DeviceService(db)
    try:
        return await service.assign_device(device_id, request.assigned_to)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
