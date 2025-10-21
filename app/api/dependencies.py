from collections.abc import AsyncGenerator

from fastapi import Depends

from app.services.metrics_manager import MetricManager
from app.services.sensors_manager import SensorManager
from app.storage.interfaces.metric_repository import MetricRepository
from app.storage.interfaces.sensor_repository import SensorRepository
from app.storage.repository_factory import repository_factory


async def get_sensor_repository() -> AsyncGenerator[SensorRepository, None]:
    async for repo in repository_factory.get_sensor_repository():
        yield repo


async def get_metric_repository() -> AsyncGenerator[MetricRepository, None]:
    async for repo in repository_factory.get_metric_repository():
        yield repo


async def get_sensor_manager(
    sensor_repository: SensorRepository = Depends(get_sensor_repository),
) -> SensorManager:
    return SensorManager(sensor_repository=sensor_repository)


async def get_metric_manager(
    metric_repository: MetricRepository = Depends(get_metric_repository),
    sensor_repository: SensorRepository = Depends(get_sensor_repository),
) -> MetricManager:
    return MetricManager(metric_repository=metric_repository, sensor_repository=sensor_repository)
