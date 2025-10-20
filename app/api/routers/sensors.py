from fastapi import APIRouter, Depends

from app.api.dependencies import get_sensor_manager
from app.api.models.sensor_models import SensorCreateRequest, SensorCreateResponse, SensorListResponse
from app.services.sensors_manager import SensorManager

router = APIRouter()


@router.post("", response_model=SensorCreateResponse, status_code=201)
async def create_sensor(
    sensor: SensorCreateRequest, sensor_manager: SensorManager = Depends(get_sensor_manager)
) -> SensorCreateResponse:
    """Register a new sensor in the system."""
    created_sensor = sensor_manager.create_sensor(sensor_type=sensor.sensor_type, sensor_id=sensor.sensor_id)
    return SensorCreateResponse(
        sensor_id=created_sensor.sensor_id,
        sensor_type=created_sensor.sensor_type,
        created_at=created_sensor.created_at.isoformat() + "Z",
    )


@router.get("", response_model=list[SensorListResponse])
async def list_sensors(sensor_manager: SensorManager = Depends(get_sensor_manager)) -> list[SensorListResponse]:
    """Retrieve all registered sensors."""
    business_sensors = sensor_manager.list_sensors()
    return [
        SensorListResponse(
            sensor_id=sensor.sensor_id, sensor_type=sensor.sensor_type, created_at=sensor.created_at.isoformat() + "Z"
        )
        for sensor in business_sensors
    ]
