from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.exceptions import DatabaseError
from app.shared.models import Sensor
from app.storage.database_models import SensorModel
from app.storage.interfaces.sensor_repository import SensorRepository


class PostgreSQLSensorRepository(SensorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_sensor(self, sensor: Sensor) -> Sensor:
        sensor_model = SensorModel(
            sensor_id=sensor.sensor_id,
            sensor_type=sensor.sensor_type,
            created_at=sensor.created_at,
        )

        try:
            self._session.add(sensor_model)
            await self._session.commit()
            return sensor
        except IntegrityError as e:
            await self._session.rollback()
            raise DatabaseError(
                f"Failed to create sensor: sensor with ID '{sensor.sensor_id}' may already exist"
            ) from e
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise DatabaseError(f"Database error while creating sensor: {str(e)}") from e

    async def list_sensors(self) -> list[Sensor]:
        try:
            result = await self._session.execute(select(SensorModel))
            sensor_models = result.scalars().all()

            return [
                Sensor(
                    sensor_id=str(model.sensor_id),
                    sensor_type=str(model.sensor_type),
                    created_at=model.created_at,  # type: ignore[arg-type]
                )
                for model in sensor_models
            ]
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while listing sensors: {str(e)}") from e

    async def sensor_exists(self, sensor_id: str) -> bool:
        try:
            result = await self._session.execute(select(SensorModel).where(SensorModel.sensor_id == sensor_id))
            return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while checking sensor existence: {str(e)}") from e

    async def get_sensor(self, sensor_id: str) -> Sensor | None:
        try:
            result = await self._session.execute(select(SensorModel).where(SensorModel.sensor_id == sensor_id))
            sensor_model = result.scalar_one_or_none()

            if sensor_model is None:
                return None

            return Sensor(
                sensor_id=str(sensor_model.sensor_id),
                sensor_type=str(sensor_model.sensor_type),
                created_at=sensor_model.created_at,  # type: ignore[arg-type]
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while getting sensor: {str(e)}") from e
