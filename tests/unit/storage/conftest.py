from datetime import datetime, timezone

import pytest

from app.storage.database_models import SensorModel


@pytest.fixture
def sample_sensor_model(sensor_id: str, sensor_type: str, created_at: datetime) -> SensorModel:
    return SensorModel(
        sensor_id=sensor_id,
        sensor_type=sensor_type,
        created_at=created_at,
    )


@pytest.fixture
def multiple_sensor_models() -> list[SensorModel]:
    return [
        SensorModel(
            sensor_id="sensor-001",
            sensor_type="temperature",
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        ),
        SensorModel(
            sensor_id="sensor-002",
            sensor_type="humidity",
            created_at=datetime(2023, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
        ),
    ]
