from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MetricType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"


class StatisticType(str, Enum):
    MIN = "min"
    MAX = "max"
    AVG = "avg"
    SUM = "sum"


class Sensor(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=255, description="Unique sensor identifier")
    sensor_type: str = Field(..., min_length=1, max_length=100, description="Type of sensor")
    created_at: datetime


class Metric(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=255, description="Sensor identifier")
    metric_type: MetricType
    timestamp: datetime
    value: float = Field(..., ge=-1000, le=1000, description="Metric value")


class AggregatedMetricResult(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=255, description="Sensor identifier")
    metric_type: MetricType
    statistic: StatisticType
    value: float = Field(..., description="Aggregated metric value")
