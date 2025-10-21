from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.metrics_manager import MetricManager
from app.services.sensors_manager import SensorManager
from app.storage.database_config import get_db_config
from app.storage.implementations.postgresql_metric_repository import PostgreSQLMetricRepository
from app.storage.implementations.postgresql_sensor_repository import PostgreSQLSensorRepository
from app.storage.interfaces.metric_repository import MetricRepository
from app.storage.interfaces.sensor_repository import SensorRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db_config = get_db_config()
    async for session in db_config.get_session():
        yield session


async def get_sensor_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SensorRepository:
    return PostgreSQLSensorRepository(session=session)


async def get_metric_repository(
    session: AsyncSession = Depends(get_db_session),
) -> MetricRepository:
    return PostgreSQLMetricRepository(session=session)


async def get_sensor_manager(
    sensor_repository: SensorRepository = Depends(get_sensor_repository),
) -> SensorManager:
    return SensorManager(sensor_repository=sensor_repository)


async def get_metric_manager(
    metric_repository: MetricRepository = Depends(get_metric_repository),
    sensor_repository: SensorRepository = Depends(get_sensor_repository),
) -> MetricManager:
    return MetricManager(metric_repository=metric_repository, sensor_repository=sensor_repository)
