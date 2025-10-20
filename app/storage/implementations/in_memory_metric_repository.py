from datetime import datetime

from app.shared.models import AggregatedMetricResult, Metric, MetricType, StatisticType
from app.storage.interfaces.metric_repository import MetricRepository


class InMemoryMetricRepository(MetricRepository):
    def __init__(self) -> None:
        self._metrics: list[Metric] = []

    def add_metric(self, metric: Metric) -> Metric:
        self._metrics.append(metric)
        return metric

    def query_metrics(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        statistic: StatisticType | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[AggregatedMetricResult]:
        if statistic is None:
            raise ValueError("Statistic type must be specified for aggregated queries")

        # Get filtered raw metrics
        raw_metrics = self.get_raw_metrics(
            sensor_ids=sensor_ids,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
        )

        # Group metrics by sensor_id and metric_type
        grouped_metrics: dict[tuple[str, MetricType], list[float]] = {}
        for metric in raw_metrics:
            key = (metric.sensor_id, metric.metric_type)
            if key not in grouped_metrics:
                grouped_metrics[key] = []
            grouped_metrics[key].append(metric.value)

        # Calculate aggregated results
        results: list[AggregatedMetricResult] = []
        for (sensor_id, metric_type), values in grouped_metrics.items():
            aggregated_value = self._calculate_statistic(values=values, statistic=statistic)
            result = AggregatedMetricResult(
                sensor_id=sensor_id,
                metric_type=metric_type,
                statistic=statistic,
                value=aggregated_value,
            )
            results.append(result)

        return results

    def get_raw_metrics(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[Metric]:
        filtered_metrics = self._metrics.copy()

        # Filter by sensor IDs
        if sensor_ids:
            filtered_metrics = [m for m in filtered_metrics if m.sensor_id in sensor_ids]

        # Filter by metric types
        if metrics:
            filtered_metrics = [m for m in filtered_metrics if m.metric_type in metrics]

        # Filter by date range
        if start_date or end_date:
            filtered_metrics = self._filter_by_date_range(filtered_metrics, start_date, end_date)

        return filtered_metrics

    def get_metrics_by_sensor(self, sensor_id: str) -> list[Metric]:
        return [m for m in self._metrics if m.sensor_id == sensor_id]

    def get_metrics_by_type(self, metric_type: MetricType) -> list[Metric]:
        return [m for m in self._metrics if m.metric_type == metric_type]

    def _filter_by_date_range(
        self, metrics: list[Metric], start_date: str | None, end_date: str | None
    ) -> list[Metric]:
        filtered = []

        for metric in metrics:
            metric_timestamp = metric.timestamp

            if start_date:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                if metric_timestamp < start_dt:
                    continue

            if end_date:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                if metric_timestamp > end_dt:
                    continue

            filtered.append(metric)

        return filtered

    def _calculate_statistic(self, values: list[float], statistic: StatisticType) -> float:
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
