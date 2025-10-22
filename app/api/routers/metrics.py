from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_metric_manager
from app.api.models.metric_models import (
    MetricCreateRequest,
    MetricCreateResponse,
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
    try:
        return await metric_manager.record_metric(sensor_id=sensor_id, metric_request=metric)
    except SensorNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record metric: {str(e)}")


@router.get("/query", response_model=MetricQueryResponse)
async def query_metrics(
    sensor_ids: list[str] | None = Query(None, description="IDs of sensors to include"),
    metrics: list[MetricType] = Query(..., description="Metrics to query (temperature, humidity)"),
    statistic: StatisticType = Query(..., description="Statistic to calculate"),
    start_date: datetime | None = Query(None, description="Start date (ISO format)"),
    end_date: datetime | None = Query(None, description="End date (ISO format)"),
    metric_manager: MetricManager = Depends(get_metric_manager),
) -> MetricQueryResponse:
    try:
        from app.api.models.metric_models import MetricQueryRequest

        query_request = MetricQueryRequest(
            sensor_ids=sensor_ids,
            metrics=metrics,
            statistic=statistic,
            start_date=start_date,
            end_date=end_date,
        )
        return await metric_manager.query_metrics_api(query_request=query_request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query metrics: {str(e)}")
