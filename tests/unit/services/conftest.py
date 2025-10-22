from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from app.api.models.metric_models import MetricCreateRequest, MetricQueryRequest
from app.api.models.sensor_models import SensorCreateRequest
from app.shared.models import AggregatedMetricResult, Metric, MetricType, StatisticType
from app.storage.interfaces.metric_repository import MetricRepository
from app.storage.interfaces.sensor_repository import SensorRepository


@pytest.fixture
def timestamp() -> datetime:
    return datetime.now(timezone.utc)


@pytest.fixture
def value() -> float:
    return 25.5


@pytest.fixture
def sample_metric_data(sensor_id: str, metric_type: MetricType, timestamp: datetime, value: float) -> dict:
    return {
        "sensor_id": sensor_id,
        "metric_type": metric_type,
        "timestamp": timestamp,
        "value": value,
    }


@pytest.fixture
def sample_metric(sample_metric_data: dict) -> Metric:
    return Metric(**sample_metric_data)


@pytest.fixture
def sample_aggregated_result(
    sensor_id: str, metric_type: MetricType, statistic_type: StatisticType, value: float
) -> dict:
    return {
        "sensor_id": sensor_id,
        "metric_type": metric_type,
        "statistic": statistic_type,
        "value": value,
    }


@pytest.fixture
def sample_aggregated_metric(sample_aggregated_result: dict) -> AggregatedMetricResult:
    return AggregatedMetricResult(**sample_aggregated_result)


@pytest.fixture
def sensor_create_request_data(sensor_id: str, sensor_type: str) -> dict:
    return {
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
    }


@pytest.fixture
def sensor_create_request(sensor_create_request_data: dict) -> SensorCreateRequest:
    return SensorCreateRequest(**sensor_create_request_data)


@pytest.fixture
def metric_create_request_data(metric_type: MetricType, timestamp: datetime, value: float) -> dict:
    return {
        "metric_type": metric_type,
        "timestamp": timestamp,
        "value": value,
    }


@pytest.fixture
def metric_create_request(metric_create_request_data: dict) -> MetricCreateRequest:
    return MetricCreateRequest(**metric_create_request_data)


@pytest.fixture
def metric_query_request_data(sensor_id: str, metric_type: MetricType, statistic_type: StatisticType) -> dict:
    return {
        "sensor_ids": [sensor_id],
        "metrics": [metric_type],
        "statistic": statistic_type,
        "start_date": None,
        "end_date": None,
    }


@pytest.fixture
def metric_query_request(metric_query_request_data: dict) -> MetricQueryRequest:
    return MetricQueryRequest(**metric_query_request_data)


@pytest.fixture
def mock_sensor_repository() -> SensorRepository:
    return Mock(spec=SensorRepository)


@pytest.fixture
def mock_metric_repository() -> MetricRepository:
    return Mock(spec=MetricRepository)
