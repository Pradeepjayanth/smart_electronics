"""
Device Document Model
======================

Defines the structure for documents in the 'devices' MongoDB collection.
Represents electronic devices monitored by the platform.
"""

from datetime import datetime, timezone


def create_device_document(
    device_id: str,
    name: str,
    device_type: str,
    manufacturer: str = "",
    model: str = "",
    location: str = "",
    assigned_to: str = "",
    description: str = "",
    firmware_version: str = "",
    installation_date: str | None = None,
    warranty_expiry: str | None = None,
) -> dict:
    """
    Create a new device document for MongoDB insertion.

    Args:
        device_id: Unique device identifier (e.g., "DEV001").
        name: Human-readable device name.
        device_type: Type/category of the device.
        manufacturer: Device manufacturer.
        model: Device model number.
        location: Physical location of the device.
        assigned_to: User ID of the assigned operator.
        description: Free-text description.
        firmware_version: Current firmware version.
        installation_date: When the device was installed (ISO string).
        warranty_expiry: Warranty expiration date (ISO string).

    Returns:
        A dict representing the device document.
    """
    now = datetime.now(timezone.utc)
    return {
        "device_id": device_id,
        "name": name,
        "device_type": device_type,
        "manufacturer": manufacturer,
        "model": model,
        "location": location,
        "assigned_to": assigned_to,
        "description": description,
        "firmware_version": firmware_version,
        "installation_date": installation_date,
        "warranty_expiry": warranty_expiry,
        "status": "active",  # active, warning, critical, inactive, maintenance
        "health_score": 100.0,
        "last_data_received": None,
        "created_at": now,
        "updated_at": now,
    }
