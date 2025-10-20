from app.shared.models import Sensor
from app.storage.interfaces.sensor_repository import SensorRepository


class InMemorySensorRepository(SensorRepository):
    def __init__(self) -> None:
        self._sensors: list[Sensor] = []

    def add_sensor(self, sensor: Sensor) -> Sensor:
        self._sensors.append(sensor)
        return sensor

    def list_sensors(self) -> list[Sensor]:
        return self._sensors.copy()

    def sensor_exists(self, sensor_id: str) -> bool:
        return any(sensor.sensor_id == sensor_id for sensor in self._sensors)

    def get_sensor(self, sensor_id: str) -> Sensor | None:
        for sensor in self._sensors:
            if sensor.sensor_id == sensor_id:
                return sensor
        return None
