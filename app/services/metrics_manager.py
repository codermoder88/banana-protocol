from datetime import datetime

from app.api.models.metric_models import (
    MetricCreateRequest,
    MetricCreateResponse,
    MetricQueryRequest,
    MetricQueryResponse,
    MetricQueryResult,
    StatisticResult,
)
from app.shared.exceptions import SensorNotFoundError, ValidationError
from app.shared.models import AggregatedMetricResult, Metric, MetricType, StatisticType
from app.storage.interfaces.metric_repository import MetricRepository
from app.storage.interfaces.sensor_repository import SensorRepository


class MetricManager:
    def __init__(self, metric_repository: MetricRepository, sensor_repository: SensorRepository) -> None:
        self._metric_repository = metric_repository
        self._sensor_repository = sensor_repository

    async def record_metric(self, sensor_id: str, metric_request: MetricCreateRequest) -> MetricCreateResponse:
        if not await self._sensor_repository.sensor_exists(sensor_id=sensor_id):
            raise SensorNotFoundError(f"Sensor with ID '{sensor_id}' not found")

        metric = Metric(
            sensor_id=sensor_id,
            metric_type=metric_request.metric_type,
            timestamp=metric_request.timestamp,
            value=metric_request.value,
        )
        await self._metric_repository.add_metric(metric=metric)

        return MetricCreateResponse(sensor_id=sensor_id, status="data_recorded", timestamp=metric_request.timestamp)

    async def query_metrics_api(self, query_request: MetricQueryRequest) -> MetricQueryResponse:
        aggregates = await self.query_metrics(
            sensor_ids=query_request.sensor_ids,
            metrics=query_request.metrics,
            statistic=query_request.statistic,
            start_date=query_request.start_date,
            end_date=query_request.end_date,
        )

        results = [
            MetricQueryResult(
                sensor_id=agg.sensor_id,
                metric=agg.metric_type,
                stat=StatisticResult(statistic_type=query_request.statistic, value=agg.value),
            )
            for agg in aggregates
        ]

        return MetricQueryResponse(query=query_request, results=results)

    async def query_metrics(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        statistic: StatisticType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[AggregatedMetricResult]:
        if not metrics:
            raise ValidationError("At least one metric type must be specified")

        if statistic is None:
            raise ValidationError("Statistic type must be specified")

        if start_date and end_date and start_date >= end_date:
            raise ValidationError("Start date must be before end date")

        # Validate date range is between 1 and 31 days
        if start_date and end_date:
            date_range_days = (end_date - start_date).days
            if date_range_days < 1:
                raise ValidationError("Date range must be at least 1 day")
            if date_range_days > 31:
                raise ValidationError("Date range cannot exceed 31 days")

        target_sensor_ids = await self._get_target_sensor_ids(sensor_ids=sensor_ids)

        # Repository now handles aggregation directly
        return await self._metric_repository.query_metrics(
            sensor_ids=target_sensor_ids,
            metrics=metrics,
            statistic=statistic,
            start_date=start_date,
            end_date=end_date,
        )

    async def _get_target_sensor_ids(self, sensor_ids: list[str] | None) -> list[str]:
        if sensor_ids is None:
            # Note: Unsustainable for large datasets - pagination would be nice
            all_sensors = await self._sensor_repository.list_sensors()
            return [sensor.sensor_id for sensor in all_sensors]
        return sensor_ids
