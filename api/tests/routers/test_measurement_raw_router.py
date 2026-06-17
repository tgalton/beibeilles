# tests/routers/test_measurement_raw.py

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


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


# =========================================================
# POST /measurements/ingest
#
# Vérifie :
# - route accessible
# - payload accepté
# - appel du service effectué
# =========================================================
@patch(
    "app.services.measurement_raw_service.ingest_measurements",
)
def test_ingest_measurements(
    mock_ingest,
):
    mock_ingest.return_value = []

    payload = {
        "device_serial": "ESP32-001",
        "measurements": [],
    }

    response = client.post(
        "/measurements/ingest",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == []

    mock_ingest.assert_called_once()


# =========================================================
# POST /measurements/raw/ingest
#
# Même endpoint métier
# mais route historique.
#
# On vérifie qu'elle fonctionne toujours.
# =========================================================
@patch(
    "app.services.measurement_raw_service.ingest_measurements",
)
def test_ingest_measurements_raw_route(
    mock_ingest,
):
    mock_ingest.return_value = []

    payload = {
        "device_serial": "ESP32-001",
        "measurements": [],
    }

    response = client.post(
        "/measurements/raw/ingest",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == []

    mock_ingest.assert_called_once()


# =========================================================
# Validation Pydantic
#
# Si le Raspberry envoie
# un payload incomplet :
#
# FastAPI doit répondre 422.
# =========================================================
def test_ingest_measurements_invalid_payload():

    response = client.post(
        "/measurements/ingest",
        json={},
    )

    assert response.status_code == 422


# =========================================================
# GET /measurements/id/{id}
#
# Vérifie :
# - appel du service
# - sérialisation du résultat
# =========================================================
@patch(
    "app.services.measurement_raw_service.get_measurement_by_id",
)
def test_get_measurement_by_id(
    mock_get,
):
    mock_get.return_value = {
        "id": 1,
        "type": "temperature",
        "value": 24.5,
        "hive_level_id": 1,
        "sensor_device_id": 1,
        "measured_at": "2025-01-01T12:00:00Z",
    }

    response = client.get(
        "/measurements/id/1",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["type"] == "temperature"
    assert body["value"] == 24.5

    mock_get.assert_called_once()


# =========================================================
# Vérifie que l'id reçu dans l'URL
# est bien transmis au service.
# =========================================================
@patch(
    "app.services.measurement_raw_service.get_measurement_by_id",
)
def test_get_measurement_by_id_passes_id(
    mock_get,
):
    mock_get.return_value = {
        "id": 42,
        "type": "temperature",
        "value": 20,
        "hive_level_id": None,
        "sensor_device_id": 1,
        "measured_at": "2025-01-01T12:00:00Z",
    }

    response = client.get(
        "/measurements/id/42",
    )

    assert response.status_code == 200

    args = mock_get.call_args.kwargs

    assert args["measurement_id"] == 42


# =========================================================
# GET /measurements
#
# Cas nominal.
# =========================================================
@patch(
    "app.services.measurement_raw_service.get_measurements",
)
def test_get_measurements(
    mock_get,
):
    mock_get.return_value = []

    response = client.get(
        "/measurements",
    )

    assert response.status_code == 200
    assert response.json() == []

    mock_get.assert_called_once()


# =========================================================
# Vérifie la transmission
# des query params.
#
# C'est très important :
#
# si un futur refacto casse un nom
# de paramètre, ce test échouera.
# =========================================================
@patch(
    "app.services.measurement_raw_service.get_measurements",
)
def test_get_measurements_with_filters(
    mock_get,
):
    mock_get.return_value = []

    response = client.get(
        "/measurements",
        params={
            "measurement_type": "temperature",
            "hive_level_id": 12,
            "sensor_device_id": 99,
            "limit": 50,
        },
    )

    assert response.status_code == 200

    args = mock_get.call_args.kwargs

    assert args["measurement_type"] == "temperature"
    assert args["hive_level_id"] == 12
    assert args["sensor_device_id"] == 99
    assert args["limit"] == 50


# =========================================================
# Vérifie la gestion des dates.
#
# Très utile car les datetime sont
# souvent source de bugs.
# =========================================================
@patch(
    "app.services.measurement_raw_service.get_measurements",
)
def test_get_measurements_with_dates(
    mock_get,
):
    mock_get.return_value = []

    response = client.get(
        "/measurements",
        params={
            "start_at": "2025-01-01T00:00:00",
            "end_at": "2025-01-02T00:00:00",
        },
    )

    assert response.status_code == 200

    args = mock_get.call_args.kwargs

    assert args["start_at"] is not None
    assert args["end_at"] is not None
