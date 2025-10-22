from datetime import datetime

import pytest

from app.api.models.metric_models import MetricCreateRequest, MetricQueryRequest
from app.services.metrics_manager import MetricManager
from app.shared.exceptions import SensorNotFoundError
from app.shared.models import AggregatedMetricResult, Metric, MetricType, Sensor, StatisticType
from app.storage.interfaces.metric_repository import MetricRepository
from app.storage.interfaces.sensor_repository import SensorRepository


async def test_metric_manager_record_metric_success(
    mock_metric_repository: MetricRepository,
    mock_sensor_repository: SensorRepository,
    sensor_id: str,
    metric_create_request: MetricCreateRequest,
    sample_metric: Metric,
):
    # Setup mocks
    mock_sensor_repository.sensor_exists.return_value = True
    mock_metric_repository.add_metric.return_value = sample_metric

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.record_metric(sensor_id=sensor_id, metric_request=metric_create_request)

    # Verify
    mock_sensor_repository.sensor_exists.assert_called_once_with(sensor_id=sensor_id)

    # Create variables for repeated values
    expected_timestamp = metric_create_request.timestamp

    # Create expected metric for verification
    expected_metric = Metric(
        sensor_id=sensor_id,
        metric_type=metric_create_request.metric_type,
        timestamp=expected_timestamp,
        value=metric_create_request.value,
    )
    mock_metric_repository.add_metric.assert_called_once_with(metric=expected_metric)

    # Verify response
    expected_response = {
        "sensor_id": sensor_id,
        "status": "data_recorded",
        "timestamp": expected_timestamp,
    }
    assert result.model_dump() == expected_response


async def test_metric_manager_record_metric_sensor_not_found(
    mock_metric_repository: MetricRepository,
    mock_sensor_repository: SensorRepository,
    sensor_id: str,
    metric_create_request: MetricCreateRequest,
):
    # Setup mocks
    mock_sensor_repository.sensor_exists.return_value = False

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Execute and verify exception
    with pytest.raises(SensorNotFoundError):
        await manager.record_metric(sensor_id=sensor_id, metric_request=metric_create_request)

    mock_sensor_repository.sensor_exists.assert_called_once_with(sensor_id=sensor_id)
    mock_metric_repository.add_metric.assert_not_called()


async def test_metric_manager_query_metrics_api_success(
    mock_metric_repository: MetricRepository,
    mock_sensor_repository: SensorRepository,
    metric_query_request: MetricQueryRequest,
    multiple_aggregated_metrics: list[AggregatedMetricResult],
):
    # Setup mocks
    mock_metric_repository.query_metrics.return_value = multiple_aggregated_metrics

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.query_metrics_api(query_request=metric_query_request)

    # Verify
    mock_metric_repository.query_metrics.assert_called_once()
    # Check that the method was called with the correct parameters
    assert mock_metric_repository.query_metrics.called

    # Verify response structure
    expected_response = {
        "query": metric_query_request.model_dump(),
        "results": [
            {
                "sensor_id": multiple_aggregated_metrics[0].sensor_id,
                "metric": multiple_aggregated_metrics[0].metric_type,
                "stat": {
                    "statistic_type": metric_query_request.statistic,
                    "value": multiple_aggregated_metrics[0].value,
                },
            },
            {
                "sensor_id": multiple_aggregated_metrics[1].sensor_id,
                "metric": multiple_aggregated_metrics[1].metric_type,
                "stat": {
                    "statistic_type": metric_query_request.statistic,
                    "value": multiple_aggregated_metrics[1].value,
                },
            },
        ],
    }
    assert result.model_dump() == expected_response


async def test_metric_manager_query_metrics_success(
    mock_metric_repository: MetricRepository,
    mock_sensor_repository: SensorRepository,
    sensor_id: str,
    metric_type: MetricType,
    statistic_type: StatisticType,
    multiple_aggregated_metrics: list[AggregatedMetricResult],
):
    # Setup mocks
    mock_metric_repository.query_metrics.return_value = multiple_aggregated_metrics

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.query_metrics(
        sensor_ids=[sensor_id], metrics=[metric_type], statistic=statistic_type, start_date=None, end_date=None
    )

    # Verify
    assert result == multiple_aggregated_metrics
    mock_metric_repository.query_metrics.assert_called_once()
    # Check that the method was called
    assert mock_metric_repository.query_metrics.called


async def test_metric_manager_query_latest_metrics_success(
    mock_metric_repository: MetricRepository,
    mock_sensor_repository: SensorRepository,
    sensor_id: str,
    metric_type: MetricType,
    statistic_type: StatisticType,
    timestamp: datetime,
    sample_aggregated_metric: AggregatedMetricResult,
):
    # Setup mocks
    mock_metric_repository.get_latest_timestamps.return_value = {(sensor_id, metric_type): timestamp}
    mock_metric_repository.query_metrics.return_value = [sample_aggregated_metric]

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager._query_latest_metrics(
        sensor_ids=[sensor_id], metrics=[metric_type], statistic=statistic_type
    )

    # Verify
    mock_metric_repository.get_latest_timestamps.assert_called_once_with(sensor_ids=[sensor_id], metrics=[metric_type])
    mock_metric_repository.query_metrics.assert_called_once_with(
        sensor_ids=[sensor_id],
        metrics=[metric_type],
        statistic=statistic_type,
        start_date=timestamp,
        end_date=timestamp,
    )
    assert result == [sample_aggregated_metric]


async def test_metric_manager_get_target_sensor_ids_with_specific_ids(
    mock_metric_repository: MetricRepository, mock_sensor_repository: SensorRepository, sensor_id: str
):
    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager._get_target_sensor_ids(sensor_ids=[sensor_id])

    # Verify
    assert result == [sensor_id]
    mock_sensor_repository.list_sensors.assert_not_called()


async def test_metric_manager_get_target_sensor_ids_with_none(
    mock_metric_repository: MetricRepository, mock_sensor_repository: SensorRepository, multiple_sensors: list[Sensor]
):
    # Setup mocks
    mock_sensor_repository.list_sensors.return_value = multiple_sensors

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager._get_target_sensor_ids(sensor_ids=None)

    # Verify
    mock_sensor_repository.list_sensors.assert_called_once()
    expected_ids = [sensor.sensor_id for sensor in multiple_sensors]
    assert result == expected_ids


async def test_metric_manager_query_metrics_with_latest_when_no_dates(
    mock_metric_repository: MetricRepository,
    mock_sensor_repository: SensorRepository,
    sensor_id: str,
    metric_type: MetricType,
    statistic_type: StatisticType,
    timestamp: datetime,
    sample_aggregated_metric: AggregatedMetricResult,
):
    # Setup mocks
    mock_metric_repository.get_latest_timestamps.return_value = {(sensor_id, metric_type): timestamp}
    mock_metric_repository.query_metrics.return_value = [sample_aggregated_metric]

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.query_metrics(
        sensor_ids=[sensor_id], metrics=[metric_type], statistic=statistic_type, start_date=None, end_date=None
    )

    # Verify latest metrics was called
    mock_metric_repository.get_latest_timestamps.assert_called_once_with(sensor_ids=[sensor_id], metrics=[metric_type])
    assert result == [sample_aggregated_metric]


# Tests for auto-completion functionality
async def test_metric_manager_query_metrics_api_auto_completes_start_date(
    mock_metric_repository: MetricRepository,
    mock_sensor_repository: SensorRepository,
    sensor_id: str,
    metric_type: MetricType,
    statistic_type: StatisticType,
    sample_aggregated_metric: AggregatedMetricResult,
):
    """Test that MetricManager auto-completes start_date to create 31-day window."""
    from datetime import datetime, timedelta, timezone

    from app.api.models.metric_models import MetricQueryRequest

    # Setup
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    expected_end_date = start_date + timedelta(days=31)

    mock_metric_repository.query_metrics.return_value = [sample_aggregated_metric]

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Create request with only start_date
    query_request = MetricQueryRequest(
        sensor_ids=[sensor_id], metrics=[metric_type], statistic=statistic_type, start_date=start_date, end_date=None
    )

    # Execute
    result = await manager.query_metrics_api(query_request=query_request)

    # Verify auto-completion
    assert result.query.start_date == start_date
    assert result.query.end_date == expected_end_date

    # Verify repository was called with completed dates
    mock_metric_repository.query_metrics.assert_called_once_with(
        sensor_ids=[sensor_id],
        metrics=[metric_type],
        statistic=statistic_type,
        start_date=start_date,
        end_date=expected_end_date,
    )


async def test_metric_manager_query_metrics_api_auto_completes_end_date(
    mock_metric_repository: MetricRepository,
    mock_sensor_repository: SensorRepository,
    sensor_id: str,
    metric_type: MetricType,
    statistic_type: StatisticType,
    sample_aggregated_metric: AggregatedMetricResult,
):
    """Test that MetricManager auto-completes end_date to create 31-day window."""
    from datetime import datetime, timedelta, timezone

    from app.api.models.metric_models import MetricQueryRequest

    # Setup
    end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
    expected_start_date = end_date - timedelta(days=31)

    mock_metric_repository.query_metrics.return_value = [sample_aggregated_metric]

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Create request with only end_date
    query_request = MetricQueryRequest(
        sensor_ids=[sensor_id], metrics=[metric_type], statistic=statistic_type, start_date=None, end_date=end_date
    )

    # Execute
    result = await manager.query_metrics_api(query_request=query_request)

    # Verify auto-completion
    assert result.query.start_date == expected_start_date
    assert result.query.end_date == end_date

    # Verify repository was called with completed dates
    mock_metric_repository.query_metrics.assert_called_once_with(
        sensor_ids=[sensor_id],
        metrics=[metric_type],
        statistic=statistic_type,
        start_date=expected_start_date,
        end_date=end_date,
    )


async def test_metric_manager_query_metrics_api_no_auto_completion_when_both_dates(
    mock_metric_repository: MetricRepository,
    mock_sensor_repository: SensorRepository,
    sensor_id: str,
    metric_type: MetricType,
    statistic_type: StatisticType,
    sample_aggregated_metric: AggregatedMetricResult,
):
    """Test that MetricManager doesn't auto-complete when both dates are provided."""
    from datetime import datetime, timezone

    from app.api.models.metric_models import MetricQueryRequest

    # Setup
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2023, 1, 15, tzinfo=timezone.utc)

    mock_metric_repository.query_metrics.return_value = [sample_aggregated_metric]

    manager = MetricManager(metric_repository=mock_metric_repository, sensor_repository=mock_sensor_repository)

    # Create request with both dates
    query_request = MetricQueryRequest(
        sensor_ids=[sensor_id],
        metrics=[metric_type],
        statistic=statistic_type,
        start_date=start_date,
        end_date=end_date,
    )

    # Execute
    result = await manager.query_metrics_api(query_request=query_request)

    # Verify no auto-completion
    assert result.query.start_date == start_date
    assert result.query.end_date == end_date

    # Verify repository was called with original dates
    mock_metric_repository.query_metrics.assert_called_once_with(
        sensor_ids=[sensor_id],
        metrics=[metric_type],
        statistic=statistic_type,
        start_date=start_date,
        end_date=end_date,
    )
