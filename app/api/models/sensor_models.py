from datetime import datetime

from pydantic import BaseModel


class SensorCreateRequest(BaseModel):
    sensor_id: str | None = None
    sensor_type: str


class SensorCreateResponse(BaseModel):
    sensor_id: str
    sensor_type: str
    created_at: datetime


class SensorListResponse(BaseModel):
    sensor_id: str
    sensor_type: str
    created_at: datetime
