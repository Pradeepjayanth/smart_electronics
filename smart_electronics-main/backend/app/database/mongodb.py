"""
MongoDB Connection Manager
===========================

Manages the async MongoDB connection lifecycle using Motor.
Provides a singleton database instance with proper startup/shutdown hooks.
Creates required collections and indexes on first connection.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings
from app.utils.logger import logger


class MongoDB:
    """
    MongoDB connection manager.

    Handles connection lifecycle and provides access to the database instance.
    Uses Motor's async driver for non-blocking database operations.
    """

    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.database: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """
        Establish connection to MongoDB.

        Creates the Motor client, verifies connectivity with a ping,
        and initializes required collections and indexes.
        """
        settings = get_settings()
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")

        self.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
        self.database = self.client[settings.MONGODB_DB_NAME]

        # Verify connection with a ping
        try:
            await self.client.admin.command("ping")
            logger.info(
                f"Connected to MongoDB database: {settings.MONGODB_DB_NAME}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

        # Create collections and indexes
        await self._create_indexes()

    async def disconnect(self) -> None:
        """Close the MongoDB connection gracefully."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB.")

    async def _create_indexes(self) -> None:
        """
        Create indexes for all collections.

        Indexes improve query performance for frequently accessed fields.
        This runs on every startup but is idempotent — existing indexes are skipped.
        """
        try:
            # Users collection indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("username", unique=True)
            await self.database.users.create_index("role")

            # Devices collection indexes
            await self.database.devices.create_index("device_id", unique=True)
            await self.database.devices.create_index("assigned_to")
            await self.database.devices.create_index("status")

            # SensorData collection indexes (compound for time-series queries)
            await self.database.sensor_data.create_index(
                [("device_id", 1), ("timestamp", -1)]
            )
            await self.database.sensor_data.create_index("timestamp")

            # Predictions collection indexes
            await self.database.predictions.create_index(
                [("device_id", 1), ("created_at", -1)]
            )
            await self.database.predictions.create_index("risk_level")

            # ServiceHistory collection indexes
            await self.database.service_history.create_index(
                [("device_id", 1), ("service_date", -1)]
            )

            # MaintenanceLogs collection indexes
            await self.database.maintenance_logs.create_index(
                [("device_id", 1), ("log_date", -1)]
            )

            # Reports collection indexes
            await self.database.reports.create_index(
                [("report_type", 1), ("created_at", -1)]
            )

            # Notifications collection indexes
            await self.database.notifications.create_index(
                [("user_id", 1), ("is_read", 1), ("created_at", -1)]
            )
            await self.database.notifications.create_index("alert_type")

            logger.info("MongoDB indexes created successfully.")

        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise

    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Get the active database instance.

        Returns:
            AsyncIOMotorDatabase: The connected database instance.

        Raises:
            RuntimeError: If the database connection has not been established.
        """
        if self.database is None:
            raise RuntimeError(
                "Database not connected. Call connect() first."
            )
        return self.database


# Singleton instance used across the application
mongodb = MongoDB()


async def get_db() -> AsyncIOMotorDatabase:
    """
    Dependency injection function for FastAPI routes.

    Returns the active MongoDB database instance.
    Use this as a FastAPI dependency: db = Depends(get_db)

    Returns:
        AsyncIOMotorDatabase: The connected database instance.
    """
    return mongodb.get_database()
