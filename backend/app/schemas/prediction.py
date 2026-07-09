"""
Prediction Schemas
===================

Pydantic schemas for AI failure prediction API responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """Schema for prediction results in API responses."""
    id: str = Field(..., description="MongoDB document ID")
    device_id: str
    failure_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Failure probability (0-1)",
    )
    health_score: float = Field(
        ..., ge=0.0, le=100.0, description="Health score (0-100)",
    )
    risk_level: str = Field(
        ..., description="Risk level: low, medium, high, critical",
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Model confidence (0-1)",
    )
    remaining_useful_life: float = Field(
        ..., description="Estimated remaining useful life in hours",
    )
    root_cause: str = Field(..., description="Identified root cause")
    recommendation: str = Field(..., description="Maintenance recommendation")
    
    # --- Predictive Maintenance Engine ---
    maintenance_schedule: str = Field(default="Routine", description="Suggested maintenance schedule")
    recommended_spare_parts: list[str] = Field(default_factory=list, description="Parts likely needed")
    maintenance_priority: str = Field(default="Low", description="Priority: Low, Medium, High, Critical")
    expected_failure_date: Optional[str] = Field(None, description="ISO format date of expected failure")
    estimated_repair_cost: float = Field(default=0.0, description="Estimated cost in USD")
    downtime_estimation: float = Field(default=0.0, description="Estimated downtime in hours")

    # --- Environmental Analysis ---
    environment_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Operating environment score (0-100)")
    safe_operating_suggestions: list[str] = Field(default_factory=list, description="Suggestions for better environment")

    sensor_data_id: str
    model_version: str
    created_at: datetime


class PredictionListResponse(BaseModel):
    """Schema for paginated prediction list."""
    predictions: list[PredictionResponse]
    total: int
    page: int
    page_size: int
