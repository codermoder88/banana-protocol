from pydantic import BaseModel


class SensorCreateRequest(BaseModel):
    sensor_id: str | None = None


class SensorCreateResponse(BaseModel):
    sensor_id: str
    created_at: str


class SensorListResponse(BaseModel):
    sensor_id: str
    created_at: str
