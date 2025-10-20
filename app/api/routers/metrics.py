from fastapi import APIRouter, HTTPException, Query

from app.api.models.metric_models import (
    MetricCreateRequest,
    MetricCreateResponse,
    MetricQueryRequest,
    MetricQueryResponse,
    MetricQueryResult,
    MetricType,
    StatisticResult,
    StatisticType,
)

# Import the in-memory storage from database module
from app.database import metrics_db, sensors_db

router = APIRouter()


@router.post("/{sensor_id}/metrics", response_model=MetricCreateResponse, status_code=201)
async def add_sensor_metrics(sensor_id: str, metric: MetricCreateRequest) -> MetricCreateResponse:
    """Submit new measurements for a given sensor."""
    # Check if sensor exists
    sensor_exists = any(sensor.sensor_id == sensor_id for sensor in sensors_db)
    if not sensor_exists:
        raise HTTPException(status_code=404, detail="Sensor not found")

    # Store metric data
    metric_data = {
        "sensor_id": sensor_id,
        "timestamp": metric.timestamp,
        "metric_type": metric.metric_type.value,
        "value": metric.value,
    }
    metrics_db.append(metric_data)

    return MetricCreateResponse(sensor_id=sensor_id, status="data_recorded", timestamp=metric.timestamp)


@router.get("/query", response_model=MetricQueryResponse)
async def query_metrics(
    sensor_ids: list[str] | None = Query(None, description="IDs of sensors to include"),
    metrics: list[MetricType] = Query(..., description="Metrics to query (temperature, humidity)"),
    statistic: StatisticType = Query(..., description="Statistic to calculate"),
    start_date: str | None = Query(None, description="Start date (ISO format)"),
    end_date: str | None = Query(None, description="End date (ISO format)"),
) -> MetricQueryResponse:
    """Query aggregated statistics for one or more sensors and metrics within an optional date range."""

    # Build query parameters
    query_params = MetricQueryRequest(
        sensor_ids=sensor_ids, metrics=metrics, statistic=statistic, start_date=start_date, end_date=end_date
    )

    # Filter metrics by sensor_ids if provided
    # TODO: Use filtered_metrics for actual filtering logic

    # TODO: Implement date filtering
    # TODO: Implement actual aggregation logic (min, max, avg, sum)
    # For now, return mock data
    results = []
    for sensor_id in sensor_ids or [s.sensor_id for s in sensors_db]:
        for metric in metrics:
            # Mock aggregated values based on requested metrics
            mock_value = 22.3 if metric == MetricType.TEMPERATURE else 53.7

            result = MetricQueryResult(
                sensor_id=sensor_id, metric=metric, stat=StatisticResult(statistic_type=statistic, value=mock_value)
            )
            results.append(result)

    return MetricQueryResponse(query=query_params, results=results)
