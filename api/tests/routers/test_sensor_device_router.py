from fastapi import HTTPException
from unittest.mock import Mock
from unittest.mock import patch
from fastapi.testclient import TestClient
from datetime import UTC
from datetime import datetime

from app.main import app


client = TestClient(app)


# =========================================================
# Client HTTP de test FastAPI
#
# Permet de simuler :
# - GET
# - POST
# - PUT
# - DELETE
#
# Sans lancer uvicorn.
# =========================================================
client = TestClient(app)

# Fixtures fake sensor
def fake_sensor() -> dict:

    return {
        "id": 1,
        "name": "ESP32 Salon",
        "serial_number": "ABC123",
        "hive_id": 1,
        "created_at": "2025-01-01T12:00:00Z",
    }

# Test création device
@patch(
        "app.services.sensor_device_service.create_sensor_device",
)
def test_create_sensor_device(
    mock_create: Mock
) -> None:
    
    mock_create.return_value = fake_sensor()

    response = client.post(
        "/sensor-devices",
        json={
            "name": "ESP32 Salon",
            "serial_number" : "ABC123",
        },
    )

    assert response.status_code == 200

    assert response.json()["serial_number"] == "ABC123"


# Test récupération de liste device
@patch(
    "app.services.sensor_device_service.get_sensor_all_device",
)
def test_get_all_sensor_devices(
    mock_get: Mock,
) -> None:

    mock_get.return_value = [
        fake_sensor(),
    ]

    response = client.get(
        "/sensor-devices",
    )

    assert response.status_code == 200

    assert len(response.json()) == 1


# test de récupération de device par serial
@patch(
    "app.services.sensor_device_service.get_sensor_by_serial",
)
def test_get_sensor_by_serial(
    mock_get: Mock,
) -> None:

    mock_get.return_value = fake_sensor()

    response = client.get(
        "/sensor-devices/ABC123",
    )

    assert response.status_code == 200

    assert response.json()["serial_number"] == "ABC123"


# Test vérification de serial transmis au service 
@patch(
    "app.services.sensor_device_service.get_sensor_by_serial",
)
def test_get_sensor_by_serial_passes_serial(
    mock_get: Mock,
) -> None:

    mock_get.return_value = fake_sensor()

    client.get(
        "/sensor-devices/ABC123",
    )

    mock_get.assert_called_once()

    assert (
        mock_get.call_args.kwargs["serial_number"]
        == "ABC123"
    )


# Test d'association hive <-> device
@patch(
    "app.services.sensor_device_service.associate_device_with_hive",
)
def test_associate_hive(
    mock_associate: Mock,
) -> None:

    sensor = fake_sensor()
    sensor["hive_id"] = 5

    mock_associate.return_value = sensor

    response = client.post(
        "/sensor-devices/ABC123/associate-hive/5",
    )

    assert response.status_code == 200

    assert response.json()["hive_id"] == 5

# Vérification des paramètres transmis en association device <-> hive
@patch(
    "app.services.sensor_device_service.associate_device_with_hive",
)
def test_associate_hive_passes_parameters(
    mock_associate: Mock,
) -> None:

    mock_associate.return_value = fake_sensor()

    client.post(
        "/sensor-devices/ABC123/associate-hive/5",
    )

    mock_associate.assert_called_once()

    assert (
        mock_associate.call_args.kwargs["serial_number"]
        == "ABC123"
    )

    assert (
        mock_associate.call_args.kwargs["hive_id"]
        == 5
    )


# Test HTTPException Sensor not found
@patch(
    "app.services.sensor_device_service.get_sensor_by_serial",
)
def test_get_sensor_not_found(
    mock_get: Mock,
) -> None:

    mock_get.side_effect = HTTPException(
        status_code=404,
        detail="Sensor not found",
    )

    response = client.get(
        "/sensor-devices/UNKNOWN",
    )

    assert response.status_code == 404 


# TODO TGA : faire HTTPException Sensor ou hive not found