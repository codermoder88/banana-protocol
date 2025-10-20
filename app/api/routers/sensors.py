import uuid
from datetime import datetime

from fastapi import APIRouter

from app.api.models.sensor_models import SensorCreateRequest, SensorCreateResponse, SensorListResponse
from app.shared.models import Sensor
from app.storage.implementations.in_memory_sensor_repository import InMemorySensorRepository

router = APIRouter()


@router.post("", response_model=SensorCreateResponse, status_code=201)
async def create_sensor(sensor: SensorCreateRequest) -> SensorCreateResponse:
    """Register a new sensor in the system."""
    sensor_id = sensor.sensor_id if sensor.sensor_id else str(uuid.uuid4())

    business_sensor = Sensor(sensor_id=sensor_id, sensor_type=sensor.sensor_type, created_at=datetime.now())

    sensor_repository = InMemorySensorRepository()
    created_sensor = sensor_repository.add_sensor(sensor=business_sensor)
    return SensorCreateResponse(
        sensor_id=created_sensor.sensor_id,
        sensor_type=created_sensor.sensor_type,
        created_at=created_sensor.created_at.isoformat() + "Z",
    )


@router.get("", response_model=list[SensorListResponse])
async def list_sensors() -> list[SensorListResponse]:
    """Retrieve all registered sensors."""
    sensor_repository = InMemorySensorRepository()
    business_sensors = sensor_repository.list_sensors()
    return [
        SensorListResponse(
            sensor_id=sensor.sensor_id, sensor_type=sensor.sensor_type, created_at=sensor.created_at.isoformat() + "Z"
        )
        for sensor in business_sensors
    ]
