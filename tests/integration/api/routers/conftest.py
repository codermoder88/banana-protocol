from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.services.metrics_manager import MetricManager
from app.services.sensors_manager import SensorManager
from app.shared.models import MetricType
from app.storage.interfaces.metric_repository import MetricRepository
from app.storage.interfaces.sensor_repository import SensorRepository


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def mock_sensor_repository() -> SensorRepository:
    return AsyncMock(spec=SensorRepository)


@pytest.fixture
def mock_metric_repository() -> MetricRepository:
    return AsyncMock(spec=MetricRepository)


@pytest.fixture
def mock_sensor_manager() -> SensorManager:
    return AsyncMock(spec=SensorManager)


@pytest.fixture
def mock_metric_manager() -> MetricManager:
    return AsyncMock(spec=MetricManager)


@pytest.fixture
def mock_db_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sensor_create_request_data(sensor_id: str, sensor_type: str) -> dict:
    return {"sensor_id": sensor_id, "sensor_type": sensor_type}


@pytest.fixture
def metric_create_request_data(metric_type: MetricType) -> dict:
    return {"metric_type": metric_type, "timestamp": "2023-01-01T12:00:00Z", "value": 25.5}


@pytest.fixture(autouse=True)
def cleanup_dependency_overrides():
    yield
    app.dependency_overrides.clear()
