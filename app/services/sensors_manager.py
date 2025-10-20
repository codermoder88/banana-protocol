import uuid
from datetime import datetime

from app.api.models.sensor_models import SensorCreateRequest, SensorCreateResponse, SensorListResponse
from app.shared.models import Sensor
from app.storage.interfaces.sensor_repository import SensorRepository


class SensorManager:
    def __init__(self, sensor_repository: SensorRepository) -> None:
        self._sensor_repository = sensor_repository

    def create_sensor(self, sensor_request: SensorCreateRequest) -> SensorCreateResponse:
        generated_id = sensor_request.sensor_id if sensor_request.sensor_id else str(uuid.uuid4())
        sensor = Sensor(sensor_id=generated_id, sensor_type=sensor_request.sensor_type, created_at=datetime.now())
        created_sensor = self._sensor_repository.add_sensor(sensor=sensor)

        return SensorCreateResponse(
            sensor_id=created_sensor.sensor_id,
            sensor_type=created_sensor.sensor_type,
            created_at=created_sensor.created_at,
        )

    def list_sensors(self) -> list[SensorListResponse]:
        business_sensors = self._sensor_repository.list_sensors()
        return [
            SensorListResponse(
                sensor_id=sensor.sensor_id,
                sensor_type=sensor.sensor_type,
                created_at=sensor.created_at,
            )
            for sensor in business_sensors
        ]

    def sensor_exists(self, sensor_id: str) -> bool:
        return self._sensor_repository.sensor_exists(sensor_id=sensor_id)

    def get_sensor(self, sensor_id: str) -> Sensor | None:
        return self._sensor_repository.get_sensor(sensor_id=sensor_id)
