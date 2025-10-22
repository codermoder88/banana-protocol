from datetime import datetime, timedelta

from app.api.models.metric_models import (
    MetricCreateRequest,
    MetricCreateResponse,
    MetricQueryRequest,
    MetricQueryResponse,
    MetricQueryResult,
    StatisticResult,
)
from app.shared.exceptions import SensorNotFoundError
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
        # Auto-complete single dates to create a 31-day window
        start_date, end_date = self._complete_date_range(
            start_date=query_request.start_date, end_date=query_request.end_date
        )

        aggregates = await self.query_metrics(
            sensor_ids=query_request.sensor_ids,
            metrics=query_request.metrics,
            statistic=query_request.statistic,
            start_date=start_date,
            end_date=end_date,
        )

        # Create a new query request with completed dates for the response
        completed_query = MetricQueryRequest(
            sensor_ids=query_request.sensor_ids,
            metrics=query_request.metrics,
            statistic=query_request.statistic,
            start_date=start_date,
            end_date=end_date,
        )

        results = [
            MetricQueryResult(
                sensor_id=agg.sensor_id,
                metric=agg.metric_type,
                stat=StatisticResult(statistic_type=query_request.statistic, value=agg.value),
            )
            for agg in aggregates
        ]

        return MetricQueryResponse(query=completed_query, results=results)

    async def query_metrics(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        statistic: StatisticType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[AggregatedMetricResult]:
        target_sensor_ids = await self._get_target_sensor_ids(sensor_ids=sensor_ids)

        if start_date is None and end_date is None:
            if metrics is None or statistic is None:
                raise ValueError("Metrics and statistic are required for latest metrics query")
            return await self._query_latest_metrics(
                sensor_ids=target_sensor_ids,
                metrics=metrics,
                statistic=statistic,
            )

        if metrics is None or statistic is None:
            raise ValueError("Metrics and statistic are required for date range query")
        return await self._metric_repository.query_metrics(
            statistic=statistic,
            sensor_ids=target_sensor_ids,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
        )

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
                        statistic=statistic,
                        sensor_ids=[sensor_id],
                        metrics=[metric],
                        start_date=latest_timestamp,
                        end_date=latest_timestamp,
                    )
                    results.extend(latest_metrics)

        return results

    def _complete_date_range(
        self, start_date: datetime | None, end_date: datetime | None
    ) -> tuple[datetime | None, datetime | None]:
        """Auto-complete single dates to create a 31-day window."""
        if start_date is not None and end_date is not None:
            # Both dates provided - use as-is
            return start_date, end_date

        if start_date is None and end_date is None:
            # No dates provided - use as-is (will trigger latest metrics query)
            return None, None

        # Get timezone from the provided date, or use UTC as default
        tz = start_date.tzinfo if start_date else end_date.tzinfo if end_date else None
        if tz is None:
            tz = datetime.now().tzinfo

        if start_date is not None and end_date is None:
            # Only start_date provided - set end_date to 31 days later
            completed_end_date = start_date + timedelta(days=31)
            return start_date, completed_end_date

        if end_date is not None and start_date is None:
            # Only end_date provided - set start_date to 31 days earlier
            completed_start_date = end_date - timedelta(days=31)
            return completed_start_date, end_date

        # This should never happen, but return as-is
        return start_date, end_date

    async def _get_target_sensor_ids(self, sensor_ids: list[str] | None) -> list[str]:
        if sensor_ids is None:
            all_sensors = await self._sensor_repository.list_sensors()
            return [sensor.sensor_id for sensor in all_sensors]
        return sensor_ids
