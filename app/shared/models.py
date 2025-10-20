from datetime import datetime
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


class Sensor(BaseModel):
    sensor_id: str
    sensor_type: str
    created_at: datetime


class Metric(BaseModel):
    sensor_id: str
    metric_type: MetricType
    timestamp: datetime
    value: float


class AggregatedMetricResult(BaseModel):
    sensor_id: str
    metric_type: MetricType
    statistic: StatisticType
    value: float
