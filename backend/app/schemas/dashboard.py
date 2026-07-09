"""
Dashboard Schemas
==================

Pydantic schemas for dashboard aggregation API responses.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DeviceStatusSummary(BaseModel):
    """Summary of device counts by status."""
    total_devices: int = Field(..., description="Total number of devices")
    healthy_devices: int = Field(..., description="Devices in healthy state")
    warning_devices: int = Field(..., description="Devices in warning state")
    critical_devices: int = Field(..., description="Devices in critical state")
    inactive_devices: int = Field(default=0, description="Inactive devices")
    maintenance_devices: int = Field(default=0, description="Devices under maintenance")


class RecentAlert(BaseModel):
    """Schema for a recent alert on the dashboard."""
    id: str
    device_id: str
    device_name: str
    alert_type: str
    message: str
    risk_level: str
    created_at: datetime


class DashboardStatsResponse(BaseModel):
    """Schema for the main dashboard statistics response."""
    device_summary: DeviceStatusSummary
    todays_predictions: int = Field(
        ..., description="Number of predictions made today",
    )
    average_health_score: float = Field(
        ..., description="Average health score across all devices",
    )
    recent_alerts: List[RecentAlert] = Field(
        default_factory=list, description="Recent critical and warning alerts",
    )
    total_sensor_readings_today: int = Field(
        default=0, description="Total sensor readings received today",
    )
    last_updated: datetime
