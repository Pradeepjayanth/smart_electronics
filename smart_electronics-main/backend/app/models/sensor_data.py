"""
Sensor Data Document Model
============================

Defines the structure for documents in the 'sensor_data' MongoDB collection.
Stores time-series sensor readings from devices (simulators or ESP32 hardware).
"""

from datetime import datetime, timezone


def create_sensor_data_document(
    device_id: str,
    temperature: float,
    humidity: float,
    voltage: float,
    current: float,
    vibration: float,
    timestamp: datetime | None = None,
    source: str = "simulator",
) -> dict:
    """
    Create a new sensor data document for MongoDB insertion.

    The same schema works for both Python simulator and ESP32 hardware.
    The 'source' field differentiates the data origin.

    Args:
        device_id: The device that generated the reading.
        temperature: Temperature in °C (-40 to 150).
        humidity: Relative humidity in % (0 to 100).
        voltage: Voltage in V (0 to 500).
        current: Current in A (0 to 100).
        vibration: Vibration in g (0 to 50).
        timestamp: Reading timestamp (defaults to now UTC).
        source: Data source identifier ("simulator", "esp32", "api").

    Returns:
        A dict representing the sensor data document.
    """
    return {
        "device_id": device_id,
        "temperature": temperature,
        "humidity": humidity,
        "voltage": voltage,
        "current": current,
        "vibration": vibration,
        "timestamp": timestamp or datetime.now(timezone.utc),
        "source": source,
        "created_at": datetime.now(timezone.utc),
    }
