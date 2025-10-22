from datetime import datetime, timezone

import pytest

from app.shared.models import AggregatedMetricResult, MetricType, Sensor, StatisticType


@pytest.fixture
def sensor_id() -> str:
    return "sensor-001"


@pytest.fixture
def sensor_type() -> str:
    return "temperature"


@pytest.fixture
def created_at() -> datetime:
    return datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def metric_type() -> MetricType:
    return MetricType.TEMPERATURE


@pytest.fixture
def statistic_type() -> StatisticType:
    return StatisticType.AVG


@pytest.fixture
def sample_sensor_data(sensor_id: str, sensor_type: str, created_at: datetime) -> dict:
    return {
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "created_at": created_at,
    }


@pytest.fixture
def sample_sensor(sample_sensor_data: dict) -> Sensor:
    return Sensor(**sample_sensor_data)


@pytest.fixture
def multiple_sensors_data() -> list[dict]:
    return [
        {
            "sensor_id": "sensor-001",
            "sensor_type": "temperature",
            "created_at": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        },
        {
            "sensor_id": "sensor-002",
            "sensor_type": "humidity",
            "created_at": datetime(2023, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
        },
    ]


@pytest.fixture
def multiple_sensors(multiple_sensors_data: list[dict]) -> list[Sensor]:
    return [Sensor(**sensor_data) for sensor_data in multiple_sensors_data]


@pytest.fixture
def multiple_aggregated_results() -> list[dict]:
    return [
        {
            "sensor_id": "sensor-001",
            "metric_type": MetricType.TEMPERATURE,
            "statistic": StatisticType.AVG,
            "value": 25.5,
        },
        {
            "sensor_id": "sensor-002",
            "metric_type": MetricType.HUMIDITY,
            "statistic": StatisticType.AVG,
            "value": 60.0,
        },
    ]


@pytest.fixture
def multiple_aggregated_metrics(multiple_aggregated_results: list[dict]) -> list[AggregatedMetricResult]:
    return [AggregatedMetricResult(**result_data) for result_data in multiple_aggregated_results]


@pytest.fixture
def mocked_uuid() -> str:
    return "mocked-uuid-123"


@pytest.fixture
def mocked_datetime() -> datetime:
    return datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
