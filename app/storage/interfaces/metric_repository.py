from abc import ABC, abstractmethod
from datetime import datetime

from app.shared.models import AggregatedMetricResult, Metric, MetricType, StatisticType


class MetricRepository(ABC):
    @abstractmethod
    async def add_metric(self, metric: Metric) -> Metric:
        pass

    @abstractmethod
    async def query_metrics(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        statistic: StatisticType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[AggregatedMetricResult]:
        pass

    @abstractmethod
    async def get_raw_metrics(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Metric]:
        pass

    @abstractmethod
    async def get_metrics_by_sensor(self, sensor_id: str) -> list[Metric]:
        pass

    @abstractmethod
    async def get_metrics_by_type(self, metric_type: MetricType) -> list[Metric]:
        pass
