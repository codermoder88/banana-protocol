from datetime import datetime

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
from app.shared.models import Metric
from app.shared.models import MetricType as BusinessMetricType
from app.shared.models import StatisticType as BusinessStatisticType
from app.storage.implementations.in_memory_metric_repository import InMemoryMetricRepository
from app.storage.implementations.in_memory_sensor_repository import InMemorySensorRepository

router = APIRouter()


@router.post("/{sensor_id}/metrics", response_model=MetricCreateResponse, status_code=201)
async def add_sensor_metrics(sensor_id: str, metric: MetricCreateRequest) -> MetricCreateResponse:
    """Submit new measurements for a given sensor."""
    sensor_repository = InMemorySensorRepository()
    metric_repository = InMemoryMetricRepository()

    if not sensor_repository.sensor_exists(sensor_id=sensor_id):
        raise HTTPException(status_code=404, detail="Sensor not found")

    business_metric = Metric(
        sensor_id=sensor_id,
        metric_type=BusinessMetricType(metric.metric_type.value),
        timestamp=datetime.fromisoformat(metric.timestamp.replace("Z", "+00:00")),
        value=metric.value,
    )

    metric_repository.add_metric(metric=business_metric)

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

    query_params = MetricQueryRequest(
        sensor_ids=sensor_ids, metrics=metrics, statistic=statistic, start_date=start_date, end_date=end_date
    )

    sensor_repository = InMemorySensorRepository()
    metric_repository = InMemoryMetricRepository()

    if sensor_ids is None:
        all_sensors = sensor_repository.list_sensors()
        sensor_ids = [sensor.sensor_id for sensor in all_sensors]

    business_metrics = [BusinessMetricType(m.value) for m in metrics]
    business_statistic = BusinessStatisticType(statistic.value)
    filtered_metrics = metric_repository.query_metrics(
        sensor_ids=sensor_ids,
        metrics=business_metrics,
        statistic=business_statistic,
        start_date=start_date,
        end_date=end_date,
    )

    results = []
    for sensor_id in sensor_ids:
        for metric in metrics:
            sensor_metric_data = [
                m
                for m in filtered_metrics
                if m.sensor_id == sensor_id and m.metric_type == BusinessMetricType(metric.value)
            ]

            if not sensor_metric_data:
                continue

            values = [m.value for m in sensor_metric_data]
            aggregated_value = _calculate_statistic(values=values, statistic=statistic)

            result = MetricQueryResult(
                sensor_id=sensor_id,
                metric=metric,
                stat=StatisticResult(statistic_type=statistic, value=aggregated_value),
            )
            results.append(result)

    return MetricQueryResponse(query=query_params, results=results)


def _calculate_statistic(values: list[float], statistic: StatisticType) -> float:
    if not values:
        return 0.0

    match statistic:
        case StatisticType.MIN:
            return min(values)
        case StatisticType.MAX:
            return max(values)
        case StatisticType.AVG:
            return sum(values) / len(values)
        case StatisticType.SUM:
            return sum(values)
        case _:
            return 0.0

    return 0.0
