"""
Report Routes
=============

REST endpoints exposing multi-period operational report summaries
and file exports (JSON, CSV, PDF) for the frontend or administrative download.
"""

from fastapi import APIRouter, Depends, Query, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.database.mongodb import get_db
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Advanced Reports"])


@router.get(
    "/summary",
    summary="Get operational report summary",
    description="Retrieve failure, maintenance, and warranty summaries for a specific timeframe.",
)
async def get_report_summary(
    period: str = Query(default="daily", description="Timeframe: daily, weekly, monthly, yearly"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = ReportService(db)
    return await service.generate_summary_data(period=period)


@router.get(
    "/export/json",
    summary="Export report as JSON file",
    description="Download the operational summary report formatted as a JSON file.",
)
async def export_json_report(
    period: str = Query(default="daily", description="Timeframe: daily, weekly, monthly, yearly"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = ReportService(db)
    data = await service.generate_summary_data(period=period)
    json_str = service.export_as_json(data)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="report_{period}.json"'},
    )


@router.get(
    "/export/csv",
    summary="Export report as CSV spreadsheet",
    description="Download the operational summary report formatted as a CSV spreadsheet.",
)
async def export_csv_report(
    period: str = Query(default="daily", description="Timeframe: daily, weekly, monthly, yearly"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = ReportService(db)
    data = await service.generate_summary_data(period=period)
    csv_str = service.export_as_csv(data)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="report_{period}.csv"'},
    )


@router.get(
    "/export/pdf",
    summary="Export report as PDF document",
    description="Download an executive operational summary formatted as a PDF document.",
)
async def export_pdf_report(
    period: str = Query(default="daily", description="Timeframe: daily, weekly, monthly, yearly"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = ReportService(db)
    data = await service.generate_summary_data(period=period)
    pdf_bytes = service.export_as_pdf(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{period}.pdf"'},
    )
