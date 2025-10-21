from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_metric_manager
from app.api.models.metric_models import (
    MetricCreateRequest,
    MetricCreateResponse,
    MetricQueryRequest,
    MetricQueryResponse,
)
from app.services.metrics_manager import MetricManager
from app.shared.exceptions import SensorNotFoundError, ValidationError
from app.shared.models import MetricType, StatisticType

router = APIRouter()


@router.post("/{sensor_id}/metrics", response_model=MetricCreateResponse, status_code=201)
async def add_sensor_metrics(
    sensor_id: str,
    metric: MetricCreateRequest,
    metric_manager: MetricManager = Depends(get_metric_manager),
) -> MetricCreateResponse:
    """Submit new measurements for a given sensor."""
    try:
        return await metric_manager.record_metric(sensor_id=sensor_id, metric_request=metric)
    except SensorNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record metric: {str(e)}")


def _parse_date_string(date_str: str | None, field_name: str) -> datetime | None:
    """Parse and validate date string."""
    if date_str is None:
        return None

    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid {field_name} format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )


def _validate_date_range(start_dt: datetime | None, end_dt: datetime | None) -> None:
    """Validate date range constraints."""
    if start_dt and end_dt:
        if start_dt >= end_dt:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

        date_range_days = (end_dt - start_dt).days
        if date_range_days < 1:
            raise HTTPException(status_code=400, detail="Date range must be at least 1 day")
        if date_range_days > 31:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 31 days")


@router.get("/query", response_model=MetricQueryResponse)
async def query_metrics(
    sensor_ids: list[str] | None = Query(None, description="IDs of sensors to include"),
    metrics: list[MetricType] = Query(..., description="Metrics to query (temperature, humidity)"),
    statistic: StatisticType = Query(..., description="Statistic to calculate"),
    start_date: str | None = Query(None, description="Start date (ISO format)"),
    end_date: str | None = Query(None, description="End date (ISO format)"),
    metric_manager: MetricManager = Depends(get_metric_manager),
) -> MetricQueryResponse:
    """Query aggregated statistics for one or more sensors and metrics within an optional date range."""
    try:
        # Parse and validate dates
        start_dt = _parse_date_string(start_date, "start_date")
        end_dt = _parse_date_string(end_date, "end_date")

        # Validate date range
        _validate_date_range(start_dt, end_dt)

        query_request = MetricQueryRequest(
            sensor_ids=sensor_ids, metrics=metrics, statistic=statistic, start_date=start_dt, end_date=end_dt
        )
        return await metric_manager.query_metrics_api(query_request=query_request)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid query parameters: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query metrics: {str(e)}")
