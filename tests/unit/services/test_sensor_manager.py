from datetime import datetime
from unittest.mock import patch

from app.api.models.sensor_models import SensorCreateRequest
from app.services.sensors_manager import SensorManager
from app.shared.models import Sensor
from app.storage.interfaces.sensor_repository import SensorRepository


async def test_sensor_manager_create_sensor_with_provided_id_success(
    mock_sensor_repository: SensorRepository, sensor_create_request: SensorCreateRequest, sample_sensor: Sensor
):
    # Setup mocks
    mock_sensor_repository.add_sensor.return_value = sample_sensor

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.create_sensor(sensor_request=sensor_create_request)

    # Verify repository call with sensor parameter
    mock_sensor_repository.add_sensor.assert_called_once()
    call_args = mock_sensor_repository.add_sensor.call_args
    assert call_args[1]["sensor"].sensor_id == sensor_create_request.sensor_id
    assert call_args[1]["sensor"].sensor_type == sensor_create_request.sensor_type
    assert isinstance(call_args[1]["sensor"].created_at, datetime)

    # Verify response
    expected_response = sample_sensor.model_dump()
    assert result.model_dump() == expected_response


@patch("app.services.sensors_manager.datetime")
@patch("app.services.sensors_manager.uuid")
async def test_sensor_manager_create_sensor_with_generated_id_success(
    mock_uuid,
    mock_datetime,
    mock_sensor_repository: SensorRepository,
    sensor_type: str,
    mocked_uuid: str,
    mocked_datetime: datetime,
):
    # Mock the UUID and datetime functions
    mock_uuid.uuid4.return_value = mocked_uuid
    mock_datetime.now.return_value = mocked_datetime

    # Create request without sensor_id
    sensor_request = SensorCreateRequest(sensor_type=sensor_type)

    # Create expected sensor with mocked values
    expected_sensor = Sensor(
        sensor_id=mocked_uuid,
        sensor_type=sensor_type,
        created_at=mocked_datetime,
    )
    mock_sensor_repository.add_sensor.return_value = expected_sensor

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.create_sensor(sensor_request=sensor_request)

    # Verify repository was called with exact expected sensor
    mock_sensor_repository.add_sensor.assert_called_once_with(sensor=expected_sensor)

    # Verify response
    expected_response = {
        "sensor_id": mocked_uuid,
        "sensor_type": sensor_type,
        "created_at": mocked_datetime,
    }
    assert result.model_dump() == expected_response


@patch("app.services.sensors_manager.datetime")
@patch("app.services.sensors_manager.uuid")
async def test_sensor_manager_create_sensor_with_different_types(
    mock_uuid,
    mock_datetime,
    mock_sensor_repository: SensorRepository,
    sensor_id: str,
    mocked_uuid: str,
    mocked_datetime: datetime,
):
    # Mock the UUID and datetime functions
    mock_uuid.uuid4.return_value = mocked_uuid
    mock_datetime.now.return_value = mocked_datetime

    sensor_types = ["temperature", "humidity"]

    for sensor_type in sensor_types:
        # Setup fresh mock for each test
        mock_sensor_repository.reset_mock()

        # Create variables for repeated values
        expected_sensor_id = f"{sensor_id}-{sensor_type}"

        # Create expected sensor with mocked values
        expected_sensor = Sensor(
            sensor_id=expected_sensor_id,
            sensor_type=sensor_type,
            created_at=mocked_datetime,
        )
        mock_sensor_repository.add_sensor.return_value = expected_sensor

        # Create request
        sensor_request = SensorCreateRequest(sensor_id=expected_sensor_id, sensor_type=sensor_type)

        manager = SensorManager(sensor_repository=mock_sensor_repository)

        # Execute
        result = await manager.create_sensor(sensor_request=sensor_request)

        # Verify repository was called with exact expected sensor
        mock_sensor_repository.add_sensor.assert_called_once_with(sensor=expected_sensor)

        # Verify response
        expected_response = {
            "sensor_id": expected_sensor_id,
            "sensor_type": sensor_type,
            "created_at": mocked_datetime,
        }
        assert result.model_dump() == expected_response


async def test_sensor_manager_list_sensors_success(
    mock_sensor_repository: SensorRepository, multiple_sensors: list[Sensor]
):
    # Setup mocks
    mock_sensor_repository.list_sensors.return_value = multiple_sensors

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.list_sensors()

    # Verify
    mock_sensor_repository.list_sensors.assert_called_once()
    assert len(result) == len(multiple_sensors)

    # Verify response structure for each sensor
    expected_responses = [sensor.model_dump() for sensor in multiple_sensors]
    actual_responses = [sensor_response.model_dump() for sensor_response in result]
    assert actual_responses == expected_responses


async def test_sensor_manager_list_sensors_empty(mock_sensor_repository: SensorRepository):
    # Setup mocks
    mock_sensor_repository.list_sensors.return_value = []

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.list_sensors()

    # Verify
    mock_sensor_repository.list_sensors.assert_called_once()
    assert result == []


async def test_sensor_manager_sensor_exists_true(mock_sensor_repository: SensorRepository, sensor_id: str):
    # Setup mocks
    mock_sensor_repository.sensor_exists.return_value = True

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.sensor_exists(sensor_id=sensor_id)

    # Verify
    mock_sensor_repository.sensor_exists.assert_called_once_with(sensor_id=sensor_id)
    assert result is True


async def test_sensor_manager_sensor_exists_false(mock_sensor_repository: SensorRepository, sensor_id: str):
    # Setup mocks
    mock_sensor_repository.sensor_exists.return_value = False

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.sensor_exists(sensor_id=sensor_id)

    # Verify
    mock_sensor_repository.sensor_exists.assert_called_once_with(sensor_id=sensor_id)
    assert result is False


async def test_sensor_manager_get_sensor_existing(
    mock_sensor_repository: SensorRepository, sample_sensor: Sensor, sensor_id: str
):
    # Setup mocks
    mock_sensor_repository.get_sensor.return_value = sample_sensor

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.get_sensor(sensor_id=sensor_id)

    # Verify
    mock_sensor_repository.get_sensor.assert_called_once_with(sensor_id=sensor_id)
    assert result == sample_sensor


async def test_sensor_manager_get_sensor_non_existing(mock_sensor_repository: SensorRepository, sensor_id: str):
    # Setup mocks
    mock_sensor_repository.get_sensor.return_value = None

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.get_sensor(sensor_id=sensor_id)

    # Verify
    mock_sensor_repository.get_sensor.assert_called_once_with(sensor_id=sensor_id)
    assert result is None


@patch("app.services.sensors_manager.datetime")
@patch("app.services.sensors_manager.uuid")
async def test_sensor_manager_create_sensor_with_none_id_generates_uuid(
    mock_uuid,
    mock_datetime,
    mock_sensor_repository: SensorRepository,
    sensor_type: str,
    mocked_uuid: str,
    mocked_datetime: datetime,
):
    # Mock the UUID and datetime functions
    mock_uuid.uuid4.return_value = mocked_uuid
    mock_datetime.now.return_value = mocked_datetime

    # Create request with None sensor_id
    sensor_request = SensorCreateRequest(sensor_id=None, sensor_type=sensor_type)

    # Create expected sensor with mocked values
    expected_sensor = Sensor(
        sensor_id=mocked_uuid,
        sensor_type=sensor_type,
        created_at=mocked_datetime,
    )
    mock_sensor_repository.add_sensor.return_value = expected_sensor

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.create_sensor(sensor_request=sensor_request)

    # Verify repository was called with exact expected sensor
    mock_sensor_repository.add_sensor.assert_called_once_with(sensor=expected_sensor)

    # Verify response
    expected_response = {
        "sensor_id": mocked_uuid,
        "sensor_type": sensor_type,
        "created_at": mocked_datetime,
    }
    assert result.model_dump() == expected_response


@patch("app.services.sensors_manager.datetime")
@patch("app.services.sensors_manager.uuid")
async def test_sensor_manager_create_sensor_with_none_id_generates_uuid_alternative(
    mock_uuid,
    mock_datetime,
    mock_sensor_repository: SensorRepository,
    sensor_type: str,
    mocked_uuid: str,
    mocked_datetime: datetime,
):
    # Mock the UUID and datetime functions
    mock_uuid.uuid4.return_value = mocked_uuid
    mock_datetime.now.return_value = mocked_datetime

    # Create request with None sensor_id (empty string is not allowed by Pydantic validation)
    sensor_request = SensorCreateRequest(sensor_id=None, sensor_type=sensor_type)

    # Create expected sensor with mocked values
    expected_sensor = Sensor(
        sensor_id=mocked_uuid,
        sensor_type=sensor_type,
        created_at=mocked_datetime,
    )
    mock_sensor_repository.add_sensor.return_value = expected_sensor

    manager = SensorManager(sensor_repository=mock_sensor_repository)

    # Execute
    result = await manager.create_sensor(sensor_request=sensor_request)

    # Verify repository was called with exact expected sensor
    mock_sensor_repository.add_sensor.assert_called_once_with(sensor=expected_sensor)

    # Verify response
    expected_response = {
        "sensor_id": mocked_uuid,
        "sensor_type": sensor_type,
        "created_at": mocked_datetime,
    }
    assert result.model_dump() == expected_response
