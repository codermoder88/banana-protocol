from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.exceptions import DatabaseError
from app.shared.models import AggregatedMetricResult, Metric, MetricType, StatisticType
from app.storage.database_models import MetricModel
from app.storage.interfaces.metric_repository import MetricRepository


class PostgreSQLMetricRepository(MetricRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_metric(self, metric: Metric) -> Metric:
        metric_model = self._create_metric_model(metric)

        try:
            self._session.add(metric_model)
            await self._session.commit()
            return metric
        except IntegrityError as e:
            await self._session.rollback()
            return await self._handle_duplicate_metric(metric, e)
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise DatabaseError(f"Database error while adding metric: {str(e)}") from e

    async def query_metrics(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        statistic: StatisticType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[AggregatedMetricResult]:
        if statistic is None:
            raise ValueError("Statistic type must be specified for aggregated queries")

        query = self._build_aggregation_query(statistic, sensor_ids, metrics, start_date, end_date)

        try:
            result = await self._session.execute(query)
            rows = result.all()
            return self._convert_rows_to_aggregated_results(rows, statistic)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while querying metrics: {str(e)}") from e

    async def get_raw_metrics(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Metric]:
        query = self._build_filtered_query(sensor_ids, metrics, start_date, end_date)

        try:
            result = await self._session.execute(query)
            metric_models = result.scalars().all()
            return self._convert_models_to_metrics(metric_models)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while getting raw metrics: {str(e)}") from e

    async def get_metrics_by_sensor(self, sensor_id: str) -> list[Metric]:
        try:
            result = await self._session.execute(select(MetricModel).where(MetricModel.sensor_id == sensor_id))
            metric_models = result.scalars().all()
            return self._convert_models_to_metrics(metric_models)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while getting metrics by sensor: {str(e)}") from e

    async def get_metrics_by_type(self, metric_type: MetricType) -> list[Metric]:
        try:
            result = await self._session.execute(
                select(MetricModel).where(MetricModel.metric_type == metric_type.value)
            )
            metric_models = result.scalars().all()
            return self._convert_models_to_metrics(metric_models)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while getting metrics by type: {str(e)}") from e

    async def get_latest_timestamps(
        self, sensor_ids: list[str], metrics: list[MetricType]
    ) -> dict[tuple[str, MetricType], datetime]:
        try:
            metric_values = [metric.value for metric in metrics]
            query = (
                select(
                    MetricModel.sensor_id,
                    MetricModel.metric_type,
                    func.max(MetricModel.timestamp).label("latest_timestamp"),
                )
                .where(
                    and_(
                        MetricModel.sensor_id.in_(sensor_ids),
                        MetricModel.metric_type.in_(metric_values),
                    )
                )
                .group_by(MetricModel.sensor_id, MetricModel.metric_type)
            )

            result = await self._session.execute(query)
            rows = result.all()

            latest_timestamps = {}
            for row in rows:
                sensor_id = str(row.sensor_id)
                metric_type = MetricType(row.metric_type)
                latest_timestamp = row.latest_timestamp
                latest_timestamps[(sensor_id, metric_type)] = latest_timestamp

            return latest_timestamps
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while getting latest timestamps: {str(e)}") from e

    def _create_metric_model(self, metric: Metric) -> MetricModel:
        return MetricModel(
            sensor_id=metric.sensor_id,
            metric_type=metric.metric_type.value,
            timestamp=metric.timestamp,
            value=metric.value,
        )

    def _convert_models_to_metrics(self, metric_models: Sequence[MetricModel]) -> list[Metric]:
        return [
            Metric(
                sensor_id=str(model.sensor_id),
                metric_type=MetricType(model.metric_type),
                timestamp=model.timestamp,  # type: ignore[arg-type]
                value=float(model.value),
            )
            for model in metric_models
        ]

    def _convert_rows_to_aggregated_results(
        self, rows: Sequence[Any], statistic: StatisticType
    ) -> list[AggregatedMetricResult]:
        return [
            AggregatedMetricResult(
                sensor_id=row.sensor_id,
                metric_type=MetricType(row.metric_type),
                statistic=statistic,
                value=float(row.aggregated_value),
            )
            for row in rows
        ]

    def _build_aggregation_query(
        self,
        statistic: StatisticType,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> Any:
        aggregation_func = self._get_aggregation_function(statistic)
        query = select(
            MetricModel.sensor_id,
            MetricModel.metric_type,
            aggregation_func.label("aggregated_value"),
        ).group_by(MetricModel.sensor_id, MetricModel.metric_type)

        return self._apply_filters(query, sensor_ids, metrics, start_date, end_date)

    def _build_filtered_query(
        self,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> Any:
        query = select(MetricModel)
        return self._apply_filters(query, sensor_ids, metrics, start_date, end_date)

    def _apply_filters(
        self,
        query: Any,
        sensor_ids: list[str] | None = None,
        metrics: list[MetricType] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> Any:
        conditions: list[Any] = []

        if sensor_ids:
            conditions.append(MetricModel.sensor_id.in_(sensor_ids))

        if metrics:
            metric_values = [metric.value for metric in metrics]
            conditions.append(MetricModel.metric_type.in_(metric_values))

        if start_date:
            conditions.append(MetricModel.timestamp >= start_date)

        if end_date:
            conditions.append(MetricModel.timestamp <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        return query

    def _get_aggregation_function(self, statistic: StatisticType) -> Any:
        match statistic:
            case StatisticType.MIN:
                return func.min(MetricModel.value)
            case StatisticType.MAX:
                return func.max(MetricModel.value)
            case StatisticType.AVG:
                return func.avg(MetricModel.value)
            case StatisticType.SUM:
                return func.sum(MetricModel.value)
            case _:
                raise ValueError(f"Unsupported statistic type: {statistic}")

        raise ValueError(f"Unsupported statistic type: {statistic}")

    async def _handle_duplicate_metric(self, metric: Metric, error: IntegrityError) -> Metric:
        try:
            existing_metric = await self._get_metric_by_key(
                sensor_id=metric.sensor_id,
                metric_type=metric.metric_type,
                timestamp=metric.timestamp,
            )
            return existing_metric if existing_metric else metric
        except SQLAlchemyError:
            raise DatabaseError(f"Failed to add metric due to constraint violation: {str(error)}") from error

    async def _get_metric_by_key(self, sensor_id: str, metric_type: MetricType, timestamp: datetime) -> Metric | None:
        try:
            result = await self._session.execute(
                select(MetricModel).where(
                    and_(
                        MetricModel.sensor_id == sensor_id,
                        MetricModel.metric_type == metric_type.value,
                        MetricModel.timestamp == timestamp,
                    )
                )
            )
            metric_model = result.scalar_one_or_none()

            if metric_model is None:
                return None

            return Metric(
                sensor_id=str(metric_model.sensor_id),
                metric_type=MetricType(metric_model.metric_type),
                timestamp=metric_model.timestamp,  # type: ignore
                value=float(metric_model.value),
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while getting metric by key: {str(e)}") from e
