from collections.abc import Generator

from fastapi import Depends

from app.services.metrics_manager import MetricManager
from app.services.sensors_manager import SensorManager
from app.storage.implementations.in_memory_metric_repository import InMemoryMetricRepository
from app.storage.implementations.in_memory_sensor_repository import InMemorySensorRepository
from app.storage.interfaces.metric_repository import MetricRepository
from app.storage.interfaces.sensor_repository import SensorRepository


def get_sensor_repository() -> Generator[SensorRepository, None, None]:
    repo = InMemorySensorRepository()
    try:
        yield repo
    finally:
        # No teardown needed for in-memory repo. Placeholder for future DB close.
        pass


def get_metric_repository() -> Generator[MetricRepository, None, None]:
    repo = InMemoryMetricRepository()
    try:
        yield repo
    finally:
        # No teardown needed for in-memory repo. Placeholder for future DB close.
        pass


def get_sensor_manager(
    sensor_repository: SensorRepository = Depends(get_sensor_repository),
) -> SensorManager:
    return SensorManager(sensor_repository=sensor_repository)


def get_metric_manager(
    metric_repository: MetricRepository = Depends(get_metric_repository),
    sensor_repository: SensorRepository = Depends(get_sensor_repository),
) -> MetricManager:
    return MetricManager(metric_repository=metric_repository, sensor_repository=sensor_repository)
