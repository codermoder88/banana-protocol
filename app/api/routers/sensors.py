from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_sensor_manager
from app.api.models.sensor_models import SensorCreateRequest, SensorCreateResponse, SensorListResponse
from app.services.sensors_manager import SensorManager
from app.shared.exceptions import DatabaseError, ValidationError

router = APIRouter()


@router.post("", response_model=SensorCreateResponse, status_code=201)
async def create_sensor(
    sensor: SensorCreateRequest, sensor_manager: SensorManager = Depends(get_sensor_manager)
) -> SensorCreateResponse:
    """Register a new sensor in the system."""
    try:
        return await sensor_manager.create_sensor(sensor_request=sensor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except DatabaseError as e:
        raise HTTPException(status_code=409, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sensor: {str(e)}")


@router.get("", response_model=list[SensorListResponse])
async def list_sensors(sensor_manager: SensorManager = Depends(get_sensor_manager)) -> list[SensorListResponse]:
    """Retrieve all registered sensors."""
    try:
        return await sensor_manager.list_sensors()
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sensors: {str(e)}")
