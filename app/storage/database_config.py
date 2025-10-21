import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class DatabaseConfig:
    def __init__(self) -> None:
        self.database_url = self._get_database_url()
        self.engine = create_async_engine(
            url=self.database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
        )
        self.async_session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def _get_database_url(self) -> str:
        """Get database URL from environment variables."""
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        database = os.getenv("DB_NAME", "sensor_metrics")

        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        async with self.async_session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close database engine."""
        await self.engine.dispose()


class DatabaseConfigManager:
    """Manages database configuration singleton with proper lifecycle."""

    def __init__(self) -> None:
        self._config: DatabaseConfig | None = None

    def get_config(self) -> DatabaseConfig:
        """Get database configuration instance."""
        if self._config is None:
            self._config = DatabaseConfig()
        return self._config

    async def close(self) -> None:
        """Close database configuration."""
        if self._config is not None:
            await self._config.close()
            self._config = None

    def reset(self) -> None:
        """Reset database configuration (for testing)."""
        self._config = None


# Global manager instance
_db_manager = DatabaseConfigManager()


def get_db_config() -> DatabaseConfig:
    """Get database configuration instance."""
    return _db_manager.get_config()


async def close_db_config() -> None:
    """Close database configuration."""
    await _db_manager.close()


def reset_db_config() -> None:
    """Reset database configuration (for testing)."""
    _db_manager.reset()
