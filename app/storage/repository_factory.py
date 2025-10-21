from collections.abc import AsyncGenerator

from app.storage.database_config import close_db_config, get_db_config
from app.storage.implementations.postgresql_metric_repository import PostgreSQLMetricRepository
from app.storage.implementations.postgresql_sensor_repository import PostgreSQLSensorRepository
from app.storage.interfaces.metric_repository import MetricRepository
from app.storage.interfaces.sensor_repository import SensorRepository


class RepositoryFactory:
    async def get_sensor_repository(self) -> AsyncGenerator[SensorRepository, None]:
        """Get PostgreSQL sensor repository."""
        db_config = get_db_config()
        async for session in db_config.get_session():
            yield PostgreSQLSensorRepository(session=session)

    async def get_metric_repository(self) -> AsyncGenerator[MetricRepository, None]:
        """Get PostgreSQL metric repository."""
        db_config = get_db_config()
        async for session in db_config.get_session():
            yield PostgreSQLMetricRepository(session=session)

    async def close(self) -> None:
        """Close database connections."""
        await close_db_config()


# Global repository factory instance
repository_factory = RepositoryFactory()
