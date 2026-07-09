"""
Report Document Model
======================

Defines the structure for documents in the 'reports' MongoDB collection.
Stores generated daily, weekly, and monthly analytics reports.
"""

from datetime import datetime, timezone


def create_report_document(
    report_type: str,
    title: str,
    summary: str,
    data: dict,
    generated_by: str = "",
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> dict:
    """
    Create a new report document for MongoDB insertion.

    Args:
        report_type: Type of report (daily, weekly, monthly).
        title: Report title.
        summary: Executive summary of findings.
        data: Report data payload (stats, charts data, etc.).
        generated_by: User ID of who generated the report.
        period_start: Start of the reporting period.
        period_end: End of the reporting period.

    Returns:
        A dict representing the report document.
    """
    now = datetime.now(timezone.utc)
    return {
        "report_type": report_type,
        "title": title,
        "summary": summary,
        "data": data,
        "generated_by": generated_by,
        "period_start": period_start or now,
        "period_end": period_end or now,
        "format": "json",  # json, csv
        "status": "generated",  # generating, generated, failed
        "created_at": now,
    }
