"""
Sensor Data Validators
========================

Utility functions for validating sensor data ranges.
Used by the sensor data service before storing readings.

These validators are separate from Pydantic schema validators
so they can be reused in non-API contexts (e.g., batch imports).
"""


# Acceptable sensor ranges
SENSOR_RANGES = {
    "temperature": {"min": -40.0, "max": 150.0, "unit": "°C"},
    "humidity": {"min": 0.0, "max": 100.0, "unit": "%"},
    "voltage": {"min": 0.0, "max": 500.0, "unit": "V"},
    "current": {"min": 0.0, "max": 100.0, "unit": "A"},
    "vibration": {"min": 0.0, "max": 50.0, "unit": "g"},
}


def validate_sensor_reading(field: str, value: float) -> bool:
    """
    Validate a single sensor reading against its acceptable range.

    Args:
        field: The sensor field name (temperature, humidity, etc.).
        value: The sensor reading value.

    Returns:
        True if the value is within the acceptable range.

    Raises:
        ValueError: If the field is unknown or value is out of range.
    """
    if field not in SENSOR_RANGES:
        raise ValueError(f"Unknown sensor field: {field}")

    limits = SENSOR_RANGES[field]
    if not limits["min"] <= value <= limits["max"]:
        raise ValueError(
            f"{field} value {value} is out of range "
            f"[{limits['min']} — {limits['max']} {limits['unit']}]"
        )
    return True


def validate_all_sensors(data: dict) -> list[str]:
    """
    Validate all sensor readings in a data dict.

    Args:
        data: Dict with sensor field names as keys and readings as values.

    Returns:
        List of validation error messages (empty if all valid).
    """
    errors = []
    for field in SENSOR_RANGES:
        if field in data:
            try:
                validate_sensor_reading(field, data[field])
            except ValueError as e:
                errors.append(str(e))
    return errors


def get_sensor_status(data: dict) -> dict:
    """
    Determine the status of each sensor reading.

    Classifies each reading as 'normal', 'warning', or 'critical'
    based on proximity to range limits.

    Args:
        data: Dict with sensor readings.

    Returns:
        Dict mapping each sensor to its status and reading.
    """
    statuses = {}
    for field, limits in SENSOR_RANGES.items():
        if field not in data:
            continue

        value = data[field]
        range_span = limits["max"] - limits["min"]
        # Warning if within 15% of limits, critical if within 5%
        warning_threshold = range_span * 0.15
        critical_threshold = range_span * 0.05

        if (
            value <= limits["min"] + critical_threshold
            or value >= limits["max"] - critical_threshold
        ):
            status = "critical"
        elif (
            value <= limits["min"] + warning_threshold
            or value >= limits["max"] - warning_threshold
        ):
            status = "warning"
        else:
            status = "normal"

        statuses[field] = {
            "value": value,
            "status": status,
            "unit": limits["unit"],
            "min": limits["min"],
            "max": limits["max"],
        }

    return statuses
