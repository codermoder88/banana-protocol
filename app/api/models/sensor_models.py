from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SensorCreateRequest(BaseModel):
    sensor_id: str | None = Field(
        None, min_length=1, max_length=255, description="Optional sensor ID (will be generated if not provided)"
    )
    sensor_type: str = Field(..., min_length=1, max_length=100, description="Type of sensor")

    @field_validator("sensor_id")
    @classmethod
    def validate_sensor_id(cls, value: str | None) -> str | None:
        if value is not None:
            if not value or not value.strip():
                raise ValueError("Sensor ID cannot be empty")
            if not value.replace("-", "").replace("_", "").isalnum():
                raise ValueError("Sensor ID must contain only alphanumeric characters, hyphens, and underscores")
            return value.strip()
        return value

    @field_validator("sensor_type")
    @classmethod
    def validate_sensor_type(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Sensor type cannot be empty")
        return value.strip()


class SensorCreateResponse(BaseModel):
    sensor_id: str
    sensor_type: str
    created_at: datetime


class SensorListResponse(BaseModel):
    sensor_id: str
    sensor_type: str
    created_at: datetime
