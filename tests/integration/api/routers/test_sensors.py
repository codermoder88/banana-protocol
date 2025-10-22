from fastapi import status
from fastapi.testclient import TestClient

from app.api.dependencies import get_sensor_manager
from app.main import app
from app.services.sensors_manager import SensorManager
from app.shared.exceptions import DatabaseError, ValidationError
from app.shared.models import Sensor


def test_create_sensor_success(
    client: TestClient,
    sample_sensor: Sensor,
    sensor_create_request_data: dict,
    mock_sensor_manager: SensorManager,
):
    mock_sensor_manager.create_sensor.return_value = sample_sensor

    app.dependency_overrides[get_sensor_manager] = lambda: mock_sensor_manager

    response = client.post("/sensors/", json=sensor_create_request_data)

    assert response.status_code == status.HTTP_201_CREATED
    expected_response = sample_sensor.model_dump(mode="json")
    assert response.json() == expected_response


def test_create_sensor_validation_error(
    client: TestClient,
    mock_sensor_manager: SensorManager,
):
    mock_sensor_manager.create_sensor.side_effect = ValidationError("Invalid sensor data")

    sensor_data = {"sensor_id": "sensor-001", "sensor_type": "temperature"}

    app.dependency_overrides[get_sensor_manager] = lambda: mock_sensor_manager

    response = client.post("/sensors/", json=sensor_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Validation error" in response.json()["detail"]


def test_create_sensor_database_error(
    client: TestClient,
    sensor_create_request_data: dict,
    mock_sensor_manager: SensorManager,
):
    mock_sensor_manager.create_sensor.side_effect = DatabaseError("Database connection failed")

    app.dependency_overrides[get_sensor_manager] = lambda: mock_sensor_manager

    response = client.post("/sensors/", json=sensor_create_request_data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "Database error" in response.json()["detail"]


def test_create_sensor_general_error(
    client: TestClient,
    sensor_create_request_data: dict,
    mock_sensor_manager: SensorManager,
):
    mock_sensor_manager.create_sensor.side_effect = Exception("Unexpected error")

    app.dependency_overrides[get_sensor_manager] = lambda: mock_sensor_manager

    response = client.post("/sensors/", json=sensor_create_request_data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to create sensor" in response.json()["detail"]


def test_list_sensors_success(
    client: TestClient,
    multiple_sensors: list[Sensor],
    mock_sensor_manager: SensorManager,
):
    mock_sensor_manager.list_sensors.return_value = multiple_sensors

    app.dependency_overrides[get_sensor_manager] = lambda: mock_sensor_manager

    response = client.get("/sensors/")

    assert response.status_code == status.HTTP_200_OK
    expected_responses = [sensor.model_dump(mode="json") for sensor in multiple_sensors]
    assert response.json() == expected_responses


def test_list_sensors_database_error(
    client: TestClient,
    mock_sensor_manager: SensorManager,
):
    mock_sensor_manager.list_sensors.side_effect = DatabaseError("Database query failed")

    app.dependency_overrides[get_sensor_manager] = lambda: mock_sensor_manager

    response = client.get("/sensors/")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error" in response.json()["detail"]


def test_list_sensors_general_error(
    client: TestClient,
    mock_sensor_manager: SensorManager,
):
    mock_sensor_manager.list_sensors.side_effect = Exception("Unexpected error")

    app.dependency_overrides[get_sensor_manager] = lambda: mock_sensor_manager

    response = client.get("/sensors/")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to retrieve sensors" in response.json()["detail"]
