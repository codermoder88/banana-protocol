from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.storage.database_config import Base


class SensorModel(Base):
    __tablename__ = "sensors"

    sensor_id = Column(String, primary_key=True)
    sensor_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationship to metrics
    metrics = relationship("MetricModel", back_populates="sensor")


class MetricModel(Base):
    __tablename__ = "metrics"

    sensor_id = Column(String, ForeignKey("sensors.sensor_id"), nullable=False)
    metric_type = Column(ENUM("temperature", "humidity", name="metric_type_enum"), nullable=False)  # type: ignore
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(Float, nullable=False)

    # Composite primary key
    __table_args__ = (
        PrimaryKeyConstraint("sensor_id", "metric_type", "timestamp"),
        # Indexes for common query patterns
        Index("idx_metrics_sensor_id", "sensor_id"),
        Index("idx_metrics_metric_type", "metric_type"),
        Index("idx_metrics_timestamp", "timestamp"),
        Index("idx_metrics_sensor_metric", "sensor_id", "metric_type"),
        Index("idx_metrics_sensor_timestamp", "sensor_id", "timestamp"),
        Index("idx_metrics_metric_timestamp", "metric_type", "timestamp"),
        # Composite index for common aggregation queries
        Index("idx_metrics_aggregation", "sensor_id", "metric_type", "timestamp"),
    )

    # Relationship to sensor
    sensor = relationship("SensorModel", back_populates="metrics")
