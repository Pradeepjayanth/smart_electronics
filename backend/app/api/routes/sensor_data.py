"""
Sensor Data Routes
===================

Endpoints for sensor data ingestion from simulators and ESP32 hardware.
The API contract is identical for both sources.

Routes:
    POST /sensor-data              — Ingest sensor reading
    GET  /sensor-data/{device_id}  — Get sensor history
    GET  /sensor-data/{device_id}/latest — Get latest reading
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user, verify_device_auth
from app.database.mongodb import get_db
from app.schemas.sensor_data import SensorDataCreateRequest, SensorDataResponse
from app.services.sensor_data_service import SensorDataService

router = APIRouter(prefix="/sensor-data", tags=["Sensor Data"])


@router.post(
    "",
    response_model=SensorDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest sensor data",
    description=(
        "Accept a sensor reading from a simulator or ESP32 device. "
        "Validates all fields, stores in MongoDB, and updates device status."
    ),
)
async def ingest_sensor_data(
    request: SensorDataCreateRequest,
    device_auth: dict = Depends(verify_device_auth),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Ingest sensor data from any source (simulator, ESP32, API).

    Example payload:
    {
        "device_id": "DEV001",
        "temperature": 45,
        "humidity": 52,
        "voltage": 12,
        "current": 2.4,
        "vibration": 0.15,
        "timestamp": "auto"
    }
    """
    # Ensure the device ID in the payload matches the authenticated device
    if request.device_id != device_auth.get("device_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payload device_id does not match authenticated device.",
        )

    service = SensorDataService(db)
    try:
        return await service.ingest_sensor_data(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/{device_id}",
    summary="Get sensor history",
    description="Retrieve sensor data history for a specific device.",
)
async def get_sensor_history(
    device_id: str,
    start_date: str | None = Query(None, description="Start date (ISO)"),
    end_date: str | None = Query(None, description="End date (ISO)"),
    limit: int = Query(100, ge=1, le=1000),
    page: int = Query(1, ge=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get paginated sensor data history for a device."""
    service = SensorDataService(db)
    return await service.get_sensor_history(
        device_id=device_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        page=page,
    )


@router.get(
    "/{device_id}/latest",
    summary="Get latest sensor reading",
    description="Get the most recent sensor reading for a device.",
)
async def get_latest_reading(
    device_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get the latest sensor reading for a specific device."""
    service = SensorDataService(db)
    result = await service.get_latest_reading(device_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sensor data found for device '{device_id}'.",
        )
    return result
