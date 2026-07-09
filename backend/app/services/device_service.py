"""
Device Service
===============

Business logic for device CRUD operations, assignment, and search.
"""

from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.device import create_device_document
from app.schemas.device import DeviceCreateRequest, DeviceUpdateRequest
from app.utils.logger import logger


class DeviceService:
    """
    Manages electronic device lifecycle — registration, updates,
    assignment, search, and deletion.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.devices

    async def register_device(self, request: DeviceCreateRequest) -> dict:
        """
        Register a new electronic device.

        Args:
            request: Validated device registration data.

        Returns:
            The created device document.

        Raises:
            ValueError: If device_id already exists.
        """
        existing = await self.collection.find_one({"device_id": request.device_id})
        if existing:
            raise ValueError(
                f"Device with ID '{request.device_id}' already exists."
            )

        device_doc = create_device_document(
            device_id=request.device_id,
            name=request.name,
            device_type=request.device_type,
            manufacturer=request.manufacturer,
            model=request.model,
            location=request.location,
            description=request.description,
            firmware_version=request.firmware_version,
            installation_date=request.installation_date,
            warranty_expiry=request.warranty_expiry,
        )

        result = await self.collection.insert_one(device_doc)
        device_doc["_id"] = result.inserted_id

        logger.info(f"Device registered: {request.device_id}")
        return self._format_device(device_doc)

    async def get_device(self, device_id: str) -> dict:
        """
        Get device details by device_id.

        Args:
            device_id: The unique device identifier (e.g., "DEV001").

        Returns:
            Formatted device dict.

        Raises:
            ValueError: If device not found.
        """
        device = await self.collection.find_one({"device_id": device_id})
        if not device:
            raise ValueError(f"Device '{device_id}' not found.")
        return self._format_device(device)

    async def get_device_by_mongo_id(self, mongo_id: str) -> dict:
        """
        Get device by MongoDB ObjectId.

        Args:
            mongo_id: The MongoDB document ID string.

        Returns:
            Formatted device dict.

        Raises:
            ValueError: If device not found.
        """
        device = await self.collection.find_one({"_id": ObjectId(mongo_id)})
        if not device:
            raise ValueError("Device not found.")
        return self._format_device(device)

    async def update_device(
        self, device_id: str, request: DeviceUpdateRequest
    ) -> dict:
        """
        Update device details.

        Only updates provided (non-None) fields for partial updates.

        Args:
            device_id: The unique device identifier.
            request: Validated update data.

        Returns:
            Updated device dict.

        Raises:
            ValueError: If device not found or no fields to update.
        """
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        if not updates:
            raise ValueError("No fields to update.")

        updates["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.update_one(
            {"device_id": device_id},
            {"$set": updates},
        )

        if result.matched_count == 0:
            raise ValueError(f"Device '{device_id}' not found.")

        logger.info(f"Device updated: {device_id}")
        return await self.get_device(device_id)

    async def delete_device(self, device_id: str) -> dict:
        """
        Delete a device by device_id.

        Args:
            device_id: The unique device identifier.

        Returns:
            Success message.

        Raises:
            ValueError: If device not found.
        """
        result = await self.collection.delete_one({"device_id": device_id})
        if result.deleted_count == 0:
            raise ValueError(f"Device '{device_id}' not found.")

        logger.info(f"Device deleted: {device_id}")
        return {"message": f"Device '{device_id}' deleted successfully."}

    async def assign_device(self, device_id: str, assigned_to: str) -> dict:
        """
        Assign a device to a user.

        Args:
            device_id: The unique device identifier.
            assigned_to: User ID to assign the device to.

        Returns:
            Updated device dict.

        Raises:
            ValueError: If device not found.
        """
        result = await self.collection.update_one(
            {"device_id": device_id},
            {
                "$set": {
                    "assigned_to": assigned_to,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError(f"Device '{device_id}' not found.")

        logger.info(f"Device {device_id} assigned to user {assigned_to}")
        return await self.get_device(device_id)

    async def search_devices(
        self,
        query: str | None = None,
        device_type: str | None = None,
        status: str | None = None,
        location: str | None = None,
        assigned_to: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        Search and filter devices with pagination.

        Args:
            query: Free-text search on name and device_id.
            device_type: Filter by device type.
            status: Filter by device status.
            location: Filter by location.
            assigned_to: Filter by assigned user.
            page: Page number.
            page_size: Items per page.

        Returns:
            Dict with paginated devices and total count.
        """
        filter_query = {}

        if query:
            filter_query["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"device_id": {"$regex": query, "$options": "i"}},
            ]
        if device_type:
            filter_query["device_type"] = device_type
        if status:
            filter_query["status"] = status
        if location:
            filter_query["location"] = {"$regex": location, "$options": "i"}
        if assigned_to:
            filter_query["assigned_to"] = assigned_to

        total = await self.collection.count_documents(filter_query)
        skip = (page - 1) * page_size

        cursor = (
            self.collection.find(filter_query)
            .skip(skip)
            .limit(page_size)
            .sort("created_at", -1)
        )

        devices = []
        async for device in cursor:
            devices.append(self._format_device(device))

        return {
            "devices": devices,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_all_devices(self, page: int = 1, page_size: int = 20) -> dict:
        """
        Get all devices with pagination.

        Args:
            page: Page number.
            page_size: Items per page.

        Returns:
            Dict with paginated devices and total count.
        """
        return await self.search_devices(page=page, page_size=page_size)

    @staticmethod
    def _format_device(device: dict) -> dict:
        """Format a MongoDB device document for API response."""
        return {
            "id": str(device["_id"]),
            "device_id": device["device_id"],
            "name": device["name"],
            "device_type": device["device_type"],
            "manufacturer": device.get("manufacturer", ""),
            "model": device.get("model", ""),
            "location": device.get("location", ""),
            "assigned_to": device.get("assigned_to", ""),
            "description": device.get("description", ""),
            "firmware_version": device.get("firmware_version", ""),
            "installation_date": device.get("installation_date"),
            "warranty_expiry": device.get("warranty_expiry"),
            "status": device.get("status", "active"),
            "health_score": device.get("health_score", 100.0),
            "last_data_received": device.get("last_data_received"),
            "created_at": device["created_at"],
            "updated_at": device["updated_at"],
        }
