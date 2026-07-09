"""
Maintenance Log Document Model
================================

Defines the structure for documents in the 'maintenance_logs' MongoDB collection.
Tracks scheduled and unscheduled maintenance activities.
"""

from datetime import datetime, timezone


def create_maintenance_log_document(
    device_id: str,
    log_type: str,
    title: str,
    description: str,
    performed_by: str = "",
    performer_id: str = "",
    scheduled_date: datetime | None = None,
    completed_date: datetime | None = None,
    duration_hours: float = 0.0,
    priority: str = "medium",
    notes: str = "",
) -> dict:
    """
    Create a new maintenance log document for MongoDB insertion.

    Args:
        device_id: The device that was maintained.
        log_type: Type of maintenance (preventive, corrective, predictive, emergency).
        title: Short title for the log entry.
        description: Detailed description of the maintenance performed.
        performed_by: Name of the person who performed maintenance.
        performer_id: User ID of the person.
        scheduled_date: When maintenance was scheduled.
        completed_date: When maintenance was completed.
        duration_hours: Duration of maintenance in hours.
        priority: Priority level (low, medium, high, urgent).
        notes: Additional notes.

    Returns:
        A dict representing the maintenance log document.
    """
    now = datetime.now(timezone.utc)
    return {
        "device_id": device_id,
        "log_type": log_type,
        "title": title,
        "description": description,
        "performed_by": performed_by,
        "performer_id": performer_id,
        "scheduled_date": scheduled_date,
        "completed_date": completed_date,
        "duration_hours": duration_hours,
        "status": "pending",  # pending, in_progress, completed, cancelled
        "priority": priority,
        "notes": notes,
        "log_date": now,
        "created_at": now,
        "updated_at": now,
    }
