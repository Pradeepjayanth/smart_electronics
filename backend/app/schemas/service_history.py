"""
Service History Schemas
========================

Pydantic schemas for service history and maintenance log endpoints.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# --- Service History ---

class ServiceHistoryCreateRequest(BaseModel):
    """Schema for adding a new service record."""
    device_id: str = Field(..., description="Device ID")
    service_type: str = Field(
        ..., description="Service type: repair, inspection, calibration, replacement",
    )
    description: str = Field(
        ..., min_length=1, max_length=1000,
        description="Description of the service performed",
    )
    technician_name: str = Field(default="", max_length=100)
    parts_replaced: List[str] = Field(default_factory=list)
    cost: float = Field(default=0.0, ge=0.0, description="Service cost")
    warranty_covered: bool = Field(default=False)
    service_date: Optional[str] = Field(
        None, description="Service date (ISO format, defaults to now)",
    )
    notes: str = Field(default="", max_length=2000)


class ServiceHistoryUpdateRequest(BaseModel):
    """Schema for updating a service record."""
    service_type: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)
    technician_name: Optional[str] = Field(None, max_length=100)
    parts_replaced: Optional[List[str]] = None
    cost: Optional[float] = Field(None, ge=0.0)
    warranty_covered: Optional[bool] = None
    status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)


class ServiceHistoryResponse(BaseModel):
    """Schema for service history in API responses."""
    id: str
    device_id: str
    service_type: str
    description: str
    technician_name: str
    technician_id: str
    parts_replaced: List[str]
    cost: float
    warranty_covered: bool
    service_date: datetime
    status: str
    notes: str
    created_at: datetime
    updated_at: datetime


# --- Maintenance Logs ---

class MaintenanceLogCreateRequest(BaseModel):
    """Schema for adding a new maintenance log."""
    device_id: str = Field(..., description="Device ID")
    log_type: str = Field(
        ..., description="Type: preventive, corrective, predictive, emergency",
    )
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    performed_by: str = Field(default="", max_length=100)
    scheduled_date: Optional[str] = Field(None, description="ISO format")
    completed_date: Optional[str] = Field(None, description="ISO format")
    duration_hours: float = Field(default=0.0, ge=0.0)
    priority: str = Field(default="medium")
    notes: str = Field(default="", max_length=2000)


class MaintenanceLogResponse(BaseModel):
    """Schema for maintenance logs in API responses."""
    id: str
    device_id: str
    log_type: str
    title: str
    description: str
    performed_by: str
    performer_id: str
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    duration_hours: float
    status: str
    priority: str
    notes: str
    log_date: datetime
    created_at: datetime
    updated_at: datetime
