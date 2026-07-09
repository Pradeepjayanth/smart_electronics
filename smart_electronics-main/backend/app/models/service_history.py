"""
Service History Document Model
================================

Defines the structure for documents in the 'service_history' MongoDB collection.
Tracks repair records, warranty info, and technician notes for devices.
"""

from datetime import datetime, timezone


def create_service_history_document(
    device_id: str,
    service_type: str,
    description: str,
    technician_name: str = "",
    technician_id: str = "",
    parts_replaced: list | None = None,
    cost: float = 0.0,
    warranty_covered: bool = False,
    service_date: datetime | None = None,
    notes: str = "",
) -> dict:
    """
    Create a new service history document for MongoDB insertion.

    Args:
        device_id: The device that was serviced.
        service_type: Type of service (repair, inspection, calibration, replacement).
        description: Detailed description of the service performed.
        technician_name: Name of the technician who performed the service.
        technician_id: User ID of the technician.
        parts_replaced: List of parts that were replaced.
        cost: Total cost of the service.
        warranty_covered: Whether the service was covered by warranty.
        service_date: When the service was performed (defaults to now).
        notes: Additional technician notes.

    Returns:
        A dict representing the service history document.
    """
    return {
        "device_id": device_id,
        "service_type": service_type,
        "description": description,
        "technician_name": technician_name,
        "technician_id": technician_id,
        "parts_replaced": parts_replaced or [],
        "cost": cost,
        "warranty_covered": warranty_covered,
        "service_date": service_date or datetime.now(timezone.utc),
        "status": "completed",  # scheduled, in_progress, completed, cancelled
        "notes": notes,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
