"""
Sensor Data Service
====================

Business logic for sensor data ingestion, storage, and retrieval.
Handles data from both Python simulators and ESP32 hardware identically.
"""

from datetime import datetime, timezone

from dateutil import parser as date_parser
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.sensor_data import create_sensor_data_document
from app.schemas.sensor_data import SensorDataCreateRequest
from app.utils.logger import logger
from app.utils.validators import validate_all_sensors


class SensorDataService:
    """
    Manages sensor data lifecycle — ingestion, validation, storage, retrieval.

    The API contract is identical for simulator and ESP32 sources,
    enabling seamless hardware integration without code changes.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.sensor_data
        self.devices_collection = db.devices

    async def ingest_sensor_data(self, request: SensorDataCreateRequest) -> dict:
        """
        Ingest and store a sensor data reading.

        Validates all sensor ranges, parses the timestamp, stores
        the document, and updates the device's last_data_received.

        Args:
            request: Validated sensor data from the API.

        Returns:
            The stored sensor data document.

        Raises:
            ValueError: If the device doesn't exist or sensor values are invalid.
        """
        # Verify device exists
        device = await self.devices_collection.find_one(
            {"device_id": request.device_id}
        )
        if not device:
            raise ValueError(
                f"Device '{request.device_id}' not found. Register it first."
            )

        # Validate sensor ranges (double-check beyond Pydantic)
        errors = validate_all_sensors({
            "temperature": request.temperature,
            "humidity": request.humidity,
            "voltage": request.voltage,
            "current": request.current,
            "vibration": request.vibration,
        })
        if errors:
            raise ValueError(f"Sensor validation failed: {'; '.join(errors)}")

        # Parse timestamp
        timestamp = None
        if request.timestamp:
            try:
                timestamp = date_parser.parse(request.timestamp)
            except (ValueError, TypeError):
                timestamp = datetime.now(timezone.utc)
        else:
            timestamp = datetime.now(timezone.utc)

        # Create and store document
        doc = create_sensor_data_document(
            device_id=request.device_id,
            temperature=request.temperature,
            humidity=request.humidity,
            voltage=request.voltage,
            current=request.current,
            vibration=request.vibration,
            timestamp=timestamp,
            source=request.source,
        )

        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id

        # Update device's last_data_received timestamp
        await self.devices_collection.update_one(
            {"device_id": request.device_id},
            {"$set": {"last_data_received": datetime.now(timezone.utc)}},
        )

        logger.info(
            f"Sensor data ingested: device={request.device_id}, "
            f"source={request.source}"
        )

        return self._format_sensor_data(doc)

    async def get_sensor_history(
        self,
        device_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
        page: int = 1,
    ) -> dict:
        """
        Get sensor data history for a device.

        Args:
            device_id: The device identifier.
            start_date: Optional start date filter (ISO format).
            end_date: Optional end date filter (ISO format).
            limit: Maximum records per page.
            page: Page number.

        Returns:
            Paginated sensor data history.
        """
        query = {"device_id": device_id}

        # Apply date filters
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = date_parser.parse(start_date)
            if end_date:
                date_filter["$lte"] = date_parser.parse(end_date)
            query["timestamp"] = date_filter

        total = await self.collection.count_documents(query)
        skip = (page - 1) * limit

        cursor = (
            self.collection.find(query)
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        readings = []
        async for doc in cursor:
            readings.append(self._format_sensor_data(doc))

        return {
            "readings": readings,
            "total": total,
            "page": page,
            "page_size": limit,
            "device_id": device_id,
        }

    async def get_latest_reading(self, device_id: str) -> dict | None:
        """
        Get the most recent sensor reading for a device.

        Args:
            device_id: The device identifier.

        Returns:
            The latest sensor data document, or None.
        """
        doc = await self.collection.find_one(
            {"device_id": device_id},
            sort=[("timestamp", -1)],
        )
        if doc:
            return self._format_sensor_data(doc)
        return None

    @staticmethod
    def _format_sensor_data(doc: dict) -> dict:
        """Format a sensor data document for API response."""
        return {
            "id": str(doc["_id"]),
            "device_id": doc["device_id"],
            "temperature": doc["temperature"],
            "humidity": doc["humidity"],
            "voltage": doc["voltage"],
            "current": doc["current"],
            "vibration": doc["vibration"],
            "timestamp": doc["timestamp"],
            "source": doc.get("source", "simulator"),
            "created_at": doc["created_at"],
        }
