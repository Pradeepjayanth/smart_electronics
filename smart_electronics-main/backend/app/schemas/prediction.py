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
    sensor_data_id: str
    model_version: str
    created_at: datetime


class PredictionListResponse(BaseModel):
    """Schema for paginated prediction list."""
    predictions: list[PredictionResponse]
    total: int
    page: int
    page_size: int
