from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


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

    @field_validator("sensor_id")
    @classmethod
    def validate_sensor_id(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Sensor ID cannot be empty")
        if not value.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Sensor ID must contain only alphanumeric characters, hyphens, and underscores")
        return value.strip()

    @field_validator("sensor_type")
    @classmethod
    def validate_sensor_type(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Sensor type cannot be empty")
        return value.strip()


class Metric(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=255, description="Sensor identifier")
    metric_type: MetricType
    timestamp: datetime
    value: float = Field(..., description="Metric value")

    @field_validator("sensor_id")
    @classmethod
    def validate_sensor_id(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Sensor ID cannot be empty")
        return value.strip()

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: float) -> float:
        if not isinstance(value, (int, float)):
            raise ValueError("Value must be a number")
        if value < -1000 or value > 1000:
            raise ValueError("Value must be between -1000 and 1000")
        return float(value)


class AggregatedMetricResult(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=255, description="Sensor identifier")
    metric_type: MetricType
    statistic: StatisticType
    value: float = Field(..., description="Aggregated metric value")

    @field_validator("sensor_id")
    @classmethod
    def validate_sensor_id(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Sensor ID cannot be empty")
        return value.strip()

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: float) -> float:
        if not isinstance(value, (int, float)):
            raise ValueError("Value must be a number")
        return float(value)
