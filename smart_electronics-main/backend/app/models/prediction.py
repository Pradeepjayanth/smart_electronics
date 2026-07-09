"""
Prediction Document Model
===========================

Defines the structure for documents in the 'predictions' MongoDB collection.
Stores AI-generated failure predictions for devices.
"""

from datetime import datetime, timezone


def create_prediction_document(
    device_id: str,
    failure_probability: float,
    health_score: float,
    risk_level: str,
    confidence_score: float,
    remaining_useful_life: float,
    root_cause: str,
    recommendation: str,
    sensor_data_id: str = "",
    model_version: str = "1.0.0",
) -> dict:
    """
    Create a new prediction document for MongoDB insertion.

    Args:
        device_id: The device this prediction is for.
        failure_probability: Probability of failure (0.0 to 1.0).
        health_score: Overall health score (0 to 100).
        risk_level: Risk classification (low, medium, high, critical).
        confidence_score: Model confidence (0.0 to 1.0).
        remaining_useful_life: Estimated RUL in hours.
        root_cause: Identified root cause of potential failure.
        recommendation: Suggested maintenance action.
        sensor_data_id: Reference to the sensor data used for prediction.
        model_version: Version of the ML model used.

    Returns:
        A dict representing the prediction document.
    """
    return {
        "device_id": device_id,
        "failure_probability": failure_probability,
        "health_score": health_score,
        "risk_level": risk_level,
        "confidence_score": confidence_score,
        "remaining_useful_life": remaining_useful_life,
        "root_cause": root_cause,
        "recommendation": recommendation,
        "sensor_data_id": sensor_data_id,
        "model_version": model_version,
        "created_at": datetime.now(timezone.utc),
    }
