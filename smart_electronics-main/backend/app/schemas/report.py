"""
Report Schemas
===============

Pydantic schemas for report generation and export endpoints.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    """Schema for generating a new report."""
    report_type: str = Field(
        ..., description="Report type: daily, weekly, monthly",
    )
    title: Optional[str] = Field(
        None, max_length=200,
        description="Custom report title (auto-generated if omitted)",
    )
    period_start: Optional[str] = Field(
        None, description="Period start date (ISO format)",
    )
    period_end: Optional[str] = Field(
        None, description="Period end date (ISO format)",
    )


class ReportResponse(BaseModel):
    """Schema for report data in API responses."""
    id: str
    report_type: str
    title: str
    summary: str
    data: Dict[str, Any]
    generated_by: str
    period_start: datetime
    period_end: datetime
    format: str
    status: str
    created_at: datetime


class ReportListResponse(BaseModel):
    """Schema for paginated report list."""
    reports: list[ReportResponse]
    total: int
    page: int
    page_size: int
