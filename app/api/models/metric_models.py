from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.shared.models import MetricType, StatisticType


class MetricCreateRequest(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp of the metric measurement")
    metric_type: MetricType = Field(..., description="Type of metric (temperature or humidity)")
    value: float = Field(..., description="Metric value")

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: float) -> float:
        if not isinstance(value, (int, float)):
            raise ValueError("Value must be a number")
        if value < -1000 or value > 1000:
            raise ValueError("Value must be between -1000 and 1000")
        return float(value)


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
