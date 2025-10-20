from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_metric_manager
from app.api.models.metric_models import (
    MetricCreateRequest,
    MetricCreateResponse,
    MetricQueryRequest,
    MetricQueryResponse,
    MetricQueryResult,
)
from app.api.models.metric_models import MetricType as APIMetricType
from app.api.models.metric_models import (
    StatisticResult,
)
from app.api.models.metric_models import StatisticType as APIStatisticType
from app.services.metrics_manager import MetricManager
from app.shared.models import MetricType, StatisticType

router = APIRouter()


@router.post("/{sensor_id}/metrics", response_model=MetricCreateResponse, status_code=201)
async def add_sensor_metrics(
    sensor_id: str,
    metric: MetricCreateRequest,
    metric_manager: MetricManager = Depends(get_metric_manager),
) -> MetricCreateResponse:
    """Submit new measurements for a given sensor."""
    try:
        metric_manager.record_metric(
            sensor_id=sensor_id,
            metric_type=MetricType(metric.metric_type.value),
            timestamp=datetime.fromisoformat(metric.timestamp.replace("Z", "+00:00")),
            value=metric.value,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Sensor not found")

    return MetricCreateResponse(sensor_id=sensor_id, status="data_recorded", timestamp=metric.timestamp)


@router.get("/query", response_model=MetricQueryResponse)
async def query_metrics(
    sensor_ids: list[str] | None = Query(None, description="IDs of sensors to include"),
    metrics: list[APIMetricType] = Query(..., description="Metrics to query (temperature, humidity)"),
    statistic: APIStatisticType = Query(..., description="Statistic to calculate"),
    start_date: str | None = Query(None, description="Start date (ISO format)"),
    end_date: str | None = Query(None, description="End date (ISO format)"),
    metric_manager: MetricManager = Depends(get_metric_manager),
) -> MetricQueryResponse:
    """Query aggregated statistics for one or more sensors and metrics within an optional date range."""

    query_params = MetricQueryRequest(
        sensor_ids=sensor_ids, metrics=metrics, statistic=statistic, start_date=start_date, end_date=end_date
    )

    business_metrics = [MetricType(m.value) for m in metrics]
    business_statistic = StatisticType(statistic.value)
    aggregates = metric_manager.query_metrics(
        sensor_ids=sensor_ids,
        metrics=business_metrics,
        statistic=business_statistic,
        start_date=start_date,
        end_date=end_date,
    )

    results = [
        MetricQueryResult(
            sensor_id=agg.sensor_id,
            metric=APIMetricType(agg.metric_type.value),
            stat=StatisticResult(statistic_type=statistic, value=agg.value),
        )
        for agg in aggregates
    ]

    return MetricQueryResponse(query=query_params, results=results)
