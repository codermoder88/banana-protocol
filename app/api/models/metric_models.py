from datetime import datetime

from pydantic import BaseModel

from app.shared.models import MetricType, StatisticType


class MetricCreateRequest(BaseModel):
    timestamp: datetime
    metric_type: MetricType
    value: float


class MetricQueryRequest(BaseModel):
    sensor_ids: list[str] | None = None
    metrics: list[MetricType]
    statistic: StatisticType
    start_date: datetime | None = None
    end_date: datetime | None = None


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
    timestamp: datetime


class MetricQueryResponse(BaseModel):
    query: MetricQueryRequest
    results: list[MetricQueryResult]
