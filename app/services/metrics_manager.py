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

        self._validate_date_range(start_date=start_date, end_date=end_date)

        target_sensor_ids = await self._get_target_sensor_ids(sensor_ids=sensor_ids)

        if start_date is None and end_date is None:
            return await self._query_latest_metrics(
                sensor_ids=target_sensor_ids,
                metrics=metrics,
                statistic=statistic,
            )
        return await self._metric_repository.query_metrics(
            sensor_ids=target_sensor_ids,
            metrics=metrics,
            statistic=statistic,
            start_date=start_date,
            end_date=end_date,
        )

    def _validate_date_range(self, start_date: datetime | None, end_date: datetime | None) -> None:
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("Start date must be before end date")

        if start_date and end_date:
            date_range_days = (end_date - start_date).days
            if date_range_days < 1:
                raise ValidationError("Date range must be at least 1 day")
            if date_range_days > 31:
                raise ValidationError("Date range cannot exceed 31 days")

    async def _query_latest_metrics(
        self,
        sensor_ids: list[str],
        metrics: list[MetricType],
        statistic: StatisticType,
    ) -> list[AggregatedMetricResult]:
        latest_timestamps = await self._metric_repository.get_latest_timestamps(sensor_ids=sensor_ids, metrics=metrics)

        results = []
        for sensor_id in sensor_ids:
            for metric in metrics:
                latest_timestamp = latest_timestamps.get((sensor_id, metric))
                if latest_timestamp is not None:
                    latest_metrics = await self._metric_repository.query_metrics(
                        sensor_ids=[sensor_id],
                        metrics=[metric],
                        statistic=statistic,
                        start_date=latest_timestamp,
                        end_date=latest_timestamp,
                    )
                    results.extend(latest_metrics)

        return results

    async def _get_target_sensor_ids(self, sensor_ids: list[str] | None) -> list[str]:
        if sensor_ids is None:
            all_sensors = await self._sensor_repository.list_sensors()
            return [sensor.sensor_id for sensor in all_sensors]
        return sensor_ids
