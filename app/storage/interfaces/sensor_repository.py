from abc import ABC, abstractmethod

from app.shared.models import Sensor


class SensorRepository(ABC):
    @abstractmethod
    def add_sensor(self, sensor: Sensor) -> Sensor:
        pass

    @abstractmethod
    def list_sensors(self) -> list[Sensor]:
        pass

    @abstractmethod
    def sensor_exists(self, sensor_id: str) -> bool:
        pass

    @abstractmethod
    def get_sensor(self, sensor_id: str) -> Sensor | None:
        pass
