import uuid
from datetime import datetime

from app.shared.models import Sensor
from app.storage.interfaces.sensor_repository import SensorRepository


class SensorManager:
    def __init__(self, sensor_repository: SensorRepository) -> None:
        self._sensor_repository = sensor_repository

    def create_sensor(self, sensor_type: str, sensor_id: str | None = None) -> Sensor:
        generated_id = sensor_id if sensor_id else str(uuid.uuid4())
        sensor = Sensor(sensor_id=generated_id, sensor_type=sensor_type, created_at=datetime.now())
        return self._sensor_repository.add_sensor(sensor=sensor)

    def list_sensors(self) -> list[Sensor]:
        return self._sensor_repository.list_sensors()

    def sensor_exists(self, sensor_id: str) -> bool:
        return self._sensor_repository.sensor_exists(sensor_id=sensor_id)

    def get_sensor(self, sensor_id: str) -> Sensor | None:
        return self._sensor_repository.get_sensor(sensor_id=sensor_id)
