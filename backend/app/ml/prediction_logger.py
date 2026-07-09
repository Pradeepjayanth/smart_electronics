"""
Prediction Logger
=================

Asynchronously logs ML predictions and generated metrics to the MongoDB database.
Ensures that all prognostic data, environmental analysis, and raw prediction values
are persisted for historical reporting and dashboard tracking.
"""

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.utils.logger import logger


class PredictionLogger:
    """Service to log ML predictions to the database."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize the logger with a MongoDB database instance.

        Args:
            db: Active AsyncIOMotorDatabase instance.
        """
        self.db = db

    async def log_prediction(self, prediction_data: dict) -> str | None:
        """
        Save a prediction result to the 'predictions' collection.

        Args:
            prediction_data: A dictionary containing the prediction metrics,
                             device ID, sensor data reference, and model version.

        Returns:
            The string representation of the inserted document's ObjectId,
            or None if the insertion failed.
        """
        # Ensure timestamp is set
        if "created_at" not in prediction_data:
            prediction_data["created_at"] = datetime.now(timezone.utc)

        try:
            result = await self.db.predictions.insert_one(prediction_data)
            logger.debug(
                f"Prediction logged successfully for device {prediction_data.get('device_id')} "
                f"with ID: {result.inserted_id}"
            )
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to log prediction to database: {e}")
            return None
