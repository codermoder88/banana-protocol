from abc import ABC, abstractmethod

from app.shared.models import Metric, MetricType, StatisticType


class MetricRepository(ABC):
    @abstractmethod
    def add_metric(self, metric: Metric) -> Metric:
        pass

    @abstractmethod
    def query_metrics(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        statistic: StatisticType | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[Metric]:
        pass

    @abstractmethod
    def get_metrics_by_sensor(self, sensor_id: str) -> list[Metric]:
        pass

    @abstractmethod
    def get_metrics_by_type(self, metric_type: MetricType) -> list[Metric]:
        pass
