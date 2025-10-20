import uuid
from datetime import datetime

from fastapi import APIRouter

from app.api.models.sensor_models import SensorCreateRequest, SensorCreateResponse, SensorListResponse
from app.database import sensors_db

router = APIRouter()

# Import databases from database module


@router.post("", response_model=SensorCreateResponse, status_code=201)
async def create_sensor(sensor: SensorCreateRequest) -> SensorCreateResponse:
    """Register a new sensor in the system."""
    # Generate UUID if not provided
    sensor_id = sensor.sensor_id if sensor.sensor_id else str(uuid.uuid4())

    new_sensor = SensorCreateResponse(sensor_id=sensor_id, created_at=datetime.now().isoformat() + "Z")

    sensors_db.append(new_sensor)

    return new_sensor


@router.get("", response_model=list[SensorListResponse])
async def list_sensors() -> list[SensorListResponse]:
    """Retrieve all registered sensors."""
    return [SensorListResponse(sensor_id=sensor.sensor_id, created_at=sensor.created_at) for sensor in sensors_db]
