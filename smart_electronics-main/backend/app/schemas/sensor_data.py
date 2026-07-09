"""
Sensor Data Schemas
====================

Pydantic schemas for sensor data ingestion from simulators and ESP32 hardware.
Includes range validation for all sensor fields.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SensorDataCreateRequest(BaseModel):
    """
    Schema for sensor data ingestion.

    Accepts data from Python simulator and ESP32 hardware identically.
    All sensor fields are validated against safe operating ranges.
    """
    device_id: str = Field(
        ..., min_length=1, max_length=50,
        description="Device identifier (e.g., DEV001)",
    )
    temperature: float = Field(
        ..., description="Temperature in °C (-40 to 150)",
    )
    humidity: float = Field(
        ..., description="Relative humidity in % (0 to 100)",
    )
    voltage: float = Field(
        ..., description="Voltage in V (0 to 500)",
    )
    current: float = Field(
        ..., description="Current in A (0 to 100)",
    )
    vibration: float = Field(
        ..., description="Vibration in g (0 to 50)",
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO format timestamp. Auto-generated if 'auto' or omitted.",
    )
    source: str = Field(
        default="simulator",
        description="Data source: simulator, esp32, api",
    )

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Temperature must be between -40°C and 150°C."""
        if not -40 <= v <= 150:
            raise ValueError("Temperature must be between -40 and 150 °C")
        return v

    @field_validator("humidity")
    @classmethod
    def validate_humidity(cls, v: float) -> float:
        """Humidity must be between 0% and 100%."""
        if not 0 <= v <= 100:
            raise ValueError("Humidity must be between 0 and 100 %")
        return v

    @field_validator("voltage")
    @classmethod
    def validate_voltage(cls, v: float) -> float:
        """Voltage must be between 0V and 500V."""
        if not 0 <= v <= 500:
            raise ValueError("Voltage must be between 0 and 500 V")
        return v

    @field_validator("current")
    @classmethod
    def validate_current(cls, v: float) -> float:
        """Current must be between 0A and 100A."""
        if not 0 <= v <= 100:
            raise ValueError("Current must be between 0 and 100 A")
        return v

    @field_validator("vibration")
    @classmethod
    def validate_vibration(cls, v: float) -> float:
        """Vibration must be between 0g and 50g."""
        if not 0 <= v <= 50:
            raise ValueError("Vibration must be between 0 and 50 g")
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: Optional[str]) -> Optional[str]:
        """Accept 'auto' or None to use server timestamp."""
        if v is not None and v.lower() == "auto":
            return None
        return v


class SensorDataResponse(BaseModel):
    """Schema for sensor data in API responses."""
    id: str = Field(..., description="MongoDB document ID")
    device_id: str
    temperature: float
    humidity: float
    voltage: float
    current: float
    vibration: float
    timestamp: datetime
    source: str
    created_at: datetime


class SensorDataQueryParams(BaseModel):
    """Schema for querying sensor data history."""
    device_id: str = Field(..., description="Device ID to query")
    start_date: Optional[str] = Field(None, description="Start date (ISO format)")
    end_date: Optional[str] = Field(None, description="End date (ISO format)")
    limit: int = Field(default=100, ge=1, le=1000, description="Max records to return")
    page: int = Field(default=1, ge=1, description="Page number")
