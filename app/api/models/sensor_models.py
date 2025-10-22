from datetime import datetime

from pydantic import BaseModel, Field


class SensorCreateRequest(BaseModel):
    sensor_id: str | None = Field(
        None, min_length=1, max_length=255, description="Optional sensor ID (will be generated if not provided)"
    )
    sensor_type: str = Field(..., min_length=1, max_length=100, description="Type of sensor")


class SensorCreateResponse(BaseModel):
    sensor_id: str
    sensor_type: str
    created_at: datetime


class SensorListResponse(BaseModel):
    sensor_id: str
    sensor_type: str
    created_at: datetime
