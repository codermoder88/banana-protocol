from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.shared.exceptions import DatabaseError
from app.shared.models import Sensor
from app.storage.database_models import SensorModel
from app.storage.implementations.postgresql_sensor_repository import PostgreSQLSensorRepository


@pytest.fixture
def repository(mock_session: Mock) -> PostgreSQLSensorRepository:
    return PostgreSQLSensorRepository(session=mock_session)


async def test_postgresql_sensor_repository_add_sensor_success(
    repository: PostgreSQLSensorRepository, sample_sensor: Sensor, mock_session: Mock
):
    # Execute
    result = await repository.add_sensor(sensor=sample_sensor)

    # Verify
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()

    # Verify the added model
    added_model = mock_session.add.call_args[0][0]
    assert isinstance(added_model, SensorModel)

    # Verify model data using dictionary comparison
    expected_model_data = sample_sensor.model_dump()
    actual_model_data = {
        "sensor_id": added_model.sensor_id,
        "sensor_type": added_model.sensor_type,
        "created_at": added_model.created_at,
    }
    assert actual_model_data == expected_model_data

    # Verify return value
    assert result == sample_sensor


async def test_postgresql_sensor_repository_add_sensor_integrity_error(
    repository: PostgreSQLSensorRepository, sample_sensor: Sensor, mock_session: Mock
):
    # Setup mock to raise IntegrityError
    mock_session.commit.side_effect = IntegrityError("statement", "params", "orig")

    # Execute and verify exception
    with pytest.raises(DatabaseError):
        await repository.add_sensor(sensor=sample_sensor)

    # Verify rollback was called
    mock_session.rollback.assert_called_once()


async def test_postgresql_sensor_repository_add_sensor_sqlalchemy_error(
    repository: PostgreSQLSensorRepository, sample_sensor: Sensor, mock_session: Mock
):
    # Setup mock to raise SQLAlchemyError
    mock_session.commit.side_effect = SQLAlchemyError("Connection lost")

    # Execute and verify exception
    with pytest.raises(DatabaseError):
        await repository.add_sensor(sensor=sample_sensor)

    # Verify rollback was called
    mock_session.rollback.assert_called_once()


async def test_postgresql_sensor_repository_list_sensors_success(
    repository: PostgreSQLSensorRepository, mock_session: Mock, multiple_sensor_models: list[SensorModel]
):
    # Setup mock result
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = multiple_sensor_models
    mock_session.execute.return_value = mock_result

    # Execute
    result = await repository.list_sensors()

    # Verify
    mock_session.execute.assert_called_once()
    assert len(result) == len(multiple_sensor_models)

    # Verify response structure
    expected_sensors = [
        {
            "sensor_id": model.sensor_id,
            "sensor_type": model.sensor_type,
            "created_at": model.created_at,
        }
        for model in multiple_sensor_models
    ]
    actual_sensors = [sensor.model_dump() for sensor in result]
    assert actual_sensors == expected_sensors


async def test_postgresql_sensor_repository_list_sensors_sqlalchemy_error(
    repository: PostgreSQLSensorRepository, mock_session: Mock
):
    # Setup mock to raise SQLAlchemyError
    mock_session.execute.side_effect = SQLAlchemyError("Query failed")

    # Execute and verify exception
    with pytest.raises(DatabaseError):
        await repository.list_sensors()


async def test_postgresql_sensor_repository_sensor_exists_true(
    repository: PostgreSQLSensorRepository, mock_session: Mock, sensor_id: str, sample_sensor_model: SensorModel
):
    # Setup mock result
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = sample_sensor_model
    mock_session.execute.return_value = mock_result

    # Execute
    result = await repository.sensor_exists(sensor_id=sensor_id)

    # Verify
    mock_session.execute.assert_called_once()
    assert result is True


async def test_postgresql_sensor_repository_sensor_exists_false(
    repository: PostgreSQLSensorRepository, mock_session: Mock, sensor_id: str
):
    # Setup mock result
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    # Execute
    result = await repository.sensor_exists(sensor_id=sensor_id)

    # Verify
    mock_session.execute.assert_called_once()
    assert result is False


async def test_postgresql_sensor_repository_sensor_exists_sqlalchemy_error(
    repository: PostgreSQLSensorRepository, mock_session: Mock, sensor_id: str
):
    # Setup mock to raise SQLAlchemyError
    mock_session.execute.side_effect = SQLAlchemyError("Query failed")

    # Execute and verify exception
    with pytest.raises(DatabaseError):
        await repository.sensor_exists(sensor_id=sensor_id)


async def test_postgresql_sensor_repository_get_sensor_success(
    repository: PostgreSQLSensorRepository, mock_session: Mock, sensor_id: str, sample_sensor_model: SensorModel
):
    # Setup mock result
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = sample_sensor_model
    mock_session.execute.return_value = mock_result

    # Execute
    result = await repository.get_sensor(sensor_id=sensor_id)

    # Verify
    mock_session.execute.assert_called_once()
    assert result is not None

    # Verify response structure
    expected_sensor = {
        "sensor_id": sample_sensor_model.sensor_id,
        "sensor_type": sample_sensor_model.sensor_type,
        "created_at": sample_sensor_model.created_at,
    }
    assert result.model_dump() == expected_sensor


async def test_postgresql_sensor_repository_get_sensor_not_found(
    repository: PostgreSQLSensorRepository, mock_session: Mock, sensor_id: str
):
    # Setup mock result
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    # Execute
    result = await repository.get_sensor(sensor_id=sensor_id)

    # Verify
    mock_session.execute.assert_called_once()
    assert result is None


async def test_postgresql_sensor_repository_get_sensor_sqlalchemy_error(
    repository: PostgreSQLSensorRepository, mock_session: Mock, sensor_id: str
):
    # Setup mock to raise SQLAlchemyError
    mock_session.execute.side_effect = SQLAlchemyError("Query failed")

    # Execute and verify exception
    with pytest.raises(DatabaseError):
        await repository.get_sensor(sensor_id=sensor_id)
