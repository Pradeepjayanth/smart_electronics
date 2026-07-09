"""
Device Schemas
===============

Pydantic schemas for device CRUD operations, assignment, and search.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DeviceCreateRequest(BaseModel):
    """Schema for registering a new device."""
    device_id: str = Field(
        ..., min_length=1, max_length=50,
        description="Unique device identifier (e.g., DEV001)",
    )
    name: str = Field(
        ..., min_length=1, max_length=100,
        description="Human-readable device name",
    )
    device_type: str = Field(
        ..., min_length=1, max_length=50,
        description="Device type/category",
    )
    manufacturer: str = Field(default="", max_length=100)
    model: str = Field(default="", max_length=100)
    location: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=500)
    firmware_version: str = Field(default="", max_length=50)
    installation_date: Optional[str] = Field(
        None, description="Installation date (ISO format)",
    )
    warranty_expiry: Optional[str] = Field(
        None, description="Warranty expiration date (ISO format)",
    )


class DeviceUpdateRequest(BaseModel):
    """Schema for updating device details."""
    name: Optional[str] = Field(None, max_length=100)
    device_type: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    firmware_version: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, description="Device status")
    installation_date: Optional[str] = None
    warranty_expiry: Optional[str] = None


class DeviceAssignRequest(BaseModel):
    """Schema for assigning a device to a user."""
    assigned_to: str = Field(
        ..., description="User ID to assign the device to",
    )


class DeviceResponse(BaseModel):
    """Schema for device data in API responses."""
    id: str = Field(..., description="MongoDB document ID")
    device_id: str
    name: str
    device_type: str
    manufacturer: str
    model: str
    location: str
    assigned_to: str
    description: str
    firmware_version: str
    installation_date: Optional[str] = None
    warranty_expiry: Optional[str] = None
    status: str
    health_score: float
    last_data_received: Optional[datetime] = None
    api_key: str
    created_at: datetime
    updated_at: datetime

class DeviceRegistrationResponse(DeviceResponse):
    """Schema returned only once upon successful registration, containing secrets."""
    device_token: str = Field(..., description="Token for the ESP32 device")
    device_secret: str = Field(..., description="Secret key for the ESP32 device (Show once!)")


class DeviceSearchQuery(BaseModel):
    """Schema for device search parameters."""
    query: Optional[str] = Field(None, description="Search by name or device_id")
    device_type: Optional[str] = Field(None, description="Filter by type")
    status: Optional[str] = Field(None, description="Filter by status")
    location: Optional[str] = Field(None, description="Filter by location")
    assigned_to: Optional[str] = Field(None, description="Filter by assignee")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
