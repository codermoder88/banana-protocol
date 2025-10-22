from fastapi import status
from fastapi.testclient import TestClient

from app.api.dependencies import get_metric_manager
from app.main import app
from app.services.metrics_manager import MetricManager
from app.shared.exceptions import SensorNotFoundError, ValidationError
from app.shared.models import MetricType, StatisticType


def test_add_sensor_metrics_success(
    client: TestClient,
    sensor_id: str,
    metric_create_request_data: dict,
    mock_metric_manager: MetricManager,
):
    metric_response = {"sensor_id": sensor_id, "status": "data_recorded", "timestamp": "2023-01-01T12:00:00Z"}
    mock_metric_manager.record_metric.return_value = metric_response

    app.dependency_overrides[get_metric_manager] = lambda: mock_metric_manager

    response = client.post(f"/metrics/{sensor_id}/metrics", json=metric_create_request_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == metric_response


def test_add_sensor_metrics_sensor_not_found(
    client: TestClient,
    sensor_id: str,
    metric_create_request_data: dict,
    mock_metric_manager: MetricManager,
):
    mock_metric_manager.record_metric.side_effect = SensorNotFoundError(f"Sensor with ID '{sensor_id}' not found")

    app.dependency_overrides[get_metric_manager] = lambda: mock_metric_manager

    response = client.post(f"/metrics/{sensor_id}/metrics", json=metric_create_request_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert f"Sensor with ID '{sensor_id}' not found" in response.json()["detail"]


def test_add_sensor_metrics_validation_error(
    client: TestClient,
    sensor_id: str,
    mock_metric_manager: MetricManager,
):
    mock_metric_manager.record_metric.side_effect = ValidationError("Invalid metric data")

    app.dependency_overrides[get_metric_manager] = lambda: mock_metric_manager

    response = client.post(
        f"/metrics/{sensor_id}/metrics",
        json={"metric_type": "invalid", "timestamp": "2023-01-01T12:00:00Z", "value": 25.5},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    # Just check that we get a validation error response
    assert "detail" in response.json()


def test_add_sensor_metrics_general_error(
    client: TestClient,
    sensor_id: str,
    metric_create_request_data: dict,
    mock_metric_manager: MetricManager,
):
    mock_metric_manager.record_metric.side_effect = Exception("Unexpected error")

    app.dependency_overrides[get_metric_manager] = lambda: mock_metric_manager

    response = client.post(f"/metrics/{sensor_id}/metrics", json=metric_create_request_data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to record metric" in response.json()["detail"]


def test_query_metrics_success(
    client: TestClient,
    sensor_id: str,
    metric_type: MetricType,
    statistic_type: StatisticType,
    mock_metric_manager: MetricManager,
):
    from app.api.models.metric_models import MetricQueryResult, StatisticResult

    query_response = {
        "query": {
            "sensor_ids": [sensor_id],
            "metrics": [metric_type],
            "statistic": statistic_type,
            "start_date": None,
            "end_date": None,
        },
        "results": [
            MetricQueryResult(
                sensor_id=sensor_id, metric=metric_type, stat=StatisticResult(statistic_type=statistic_type, value=25.5)
            ).model_dump(),
            MetricQueryResult(
                sensor_id="sensor-002",
                metric=MetricType.HUMIDITY,
                stat=StatisticResult(statistic_type=statistic_type, value=60.0),
            ).model_dump(),
        ],
    }
    mock_metric_manager.query_metrics_api.return_value = query_response

    app.dependency_overrides[get_metric_manager] = lambda: mock_metric_manager

    response = client.get(
        "/metrics/query",
        params={
            "sensor_ids": [sensor_id],
            "metrics": [metric_type.value],
            "statistic": statistic_type.value,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == query_response


def test_query_metrics_invalid_date_format(
    client: TestClient,
    sensor_id: str,
    metric_type: MetricType,
    statistic_type: StatisticType,
    mock_metric_manager: MetricManager,
):
    app.dependency_overrides[get_metric_manager] = lambda: mock_metric_manager

    response = client.get(
        "/metrics/query",
        params={
            "sensor_ids": [sensor_id],
            "metrics": [metric_type.value],
            "statistic": statistic_type.value,
            "start_date": "invalid-date",
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to query metrics" in response.json()["detail"]


def test_query_metrics_general_error(
    client: TestClient,
    sensor_id: str,
    metric_type: MetricType,
    statistic_type: StatisticType,
    mock_metric_manager: MetricManager,
):
    mock_metric_manager.query_metrics_api.side_effect = Exception("Unexpected error")

    app.dependency_overrides[get_metric_manager] = lambda: mock_metric_manager

    response = client.get(
        "/metrics/query",
        params={
            "sensor_ids": [sensor_id],
            "metrics": [metric_type.value],
            "statistic": statistic_type.value,
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to query metrics" in response.json()["detail"]
