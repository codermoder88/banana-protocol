from abc import ABC, abstractmethod

from app.shared.models import Sensor


class SensorRepository(ABC):
    @abstractmethod
    async def add_sensor(self, sensor: Sensor) -> Sensor:
        pass

    @abstractmethod
    async def list_sensors(self) -> list[Sensor]:
        pass

    @abstractmethod
    async def sensor_exists(self, sensor_id: str) -> bool:
        pass

    @abstractmethod
    async def get_sensor(self, sensor_id: str) -> Sensor | None:
        pass
