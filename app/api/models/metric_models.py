from enum import Enum

from pydantic import BaseModel


class MetricType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"


class StatisticType(str, Enum):
    MIN = "min"
    MAX = "max"
    AVG = "avg"
    SUM = "sum"


class MetricCreateRequest(BaseModel):
    timestamp: str
    metric_type: MetricType
    value: float


class MetricQueryRequest(BaseModel):
    sensor_ids: list[str] | None = None
    metrics: list[MetricType]
    statistic: StatisticType
    start_date: str | None = None
    end_date: str | None = None


class StatisticResult(BaseModel):
    statistic_type: StatisticType
    value: float


class MetricQueryResult(BaseModel):
    sensor_id: str
    metric: MetricType
    stat: StatisticResult


class MetricCreateResponse(BaseModel):
    sensor_id: str
    status: str
    timestamp: str


class MetricQueryResponse(BaseModel):
    query: MetricQueryRequest
    results: list[MetricQueryResult]
