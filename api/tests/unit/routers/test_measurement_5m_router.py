from datetime import UTC
from datetime import datetime

from unittest.mock import Mock
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


# =========================================================
# Client HTTP de test FastAPI
#
# Permet d'appeler les endpoints
# sans lancer uvicorn.
# =========================================================
client = TestClient(app)


# =========================================================
# Fixture mesure 5 minutes.
#
# Elle respecte la structure renvoyée
# par MeasurementRead.
# =========================================================
def fake_measurement() -> dict:

    return {
        "id": 1,
        "type": "temperature",
        "value": 24.5,
        "hive_level_id": 2,
        "sensor_device_id": 10,
        "measured_at": (
            datetime.now(
                UTC,
            ).isoformat()
        ),
    }


# =========================================================
# Vérifie le fonctionnement basique
# de l'endpoint GET /measurements/5m
# =========================================================
@patch(
    "app.services.measurement_5m_service.get_measurements_5m",
)
def test_get_measurements_5m(
    mock_get: Mock,
) -> None:

    mock_get.return_value = [
        fake_measurement(),
    ]

    response = client.get(
        "/measurements/5m",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["type"] == "temperature"


# =========================================================
# Vérifie qu'un filtre simple est accepté
# et correctement transmis.
# =========================================================
@patch(
    "app.services.measurement_5m_service.get_measurements_5m",
)
def test_get_measurements_5m_with_filters(
    mock_get: Mock,
) -> None:

    mock_get.return_value = [
        fake_measurement(),
    ]

    response = client.get(
        "/measurements/5m",
        params={
            "measurement_type": "temperature",
            "hive_level_id": 2,
            "sensor_device_id": 10,
        },
    )

    assert response.status_code == 200


# =========================================================
# Vérifie que FastAPI accepte
# correctement les dates ISO.
#
# FastAPI convertit automatiquement
# les chaînes ISO en objets datetime.
# =========================================================
@patch(
    "app.services.measurement_5m_service.get_measurements_5m",
)
def test_get_measurements_5m_with_dates(
    mock_get: Mock,
) -> None:

    mock_get.return_value = [
        fake_measurement(),
    ]

    response = client.get(
        "/measurements/5m",
        params={
            "start_at": "2026-01-01T00:00:00Z",
            "end_at": "2026-01-02T00:00:00Z",
        },
    )

    assert response.status_code == 200


# =========================================================
# Vérifie que tous les paramètres
# sont correctement transmis
# au service.
#
# C'est probablement le test
# le plus important du router.
# =========================================================
@patch(
    "app.services.measurement_5m_service.get_measurements_5m",
)
def test_get_measurements_5m_passes_parameters(
    mock_get: Mock,
) -> None:

    mock_get.return_value = []

    client.get(
        "/measurements/5m",
        params={
            "measurement_type": "temperature",
            "hive_level_id": 2,
            "sensor_device_id": 10,
            "start_at": "2026-01-01T00:00:00Z",
            "end_at": "2026-01-02T00:00:00Z",
        },
    )

    mock_get.assert_called_once()

    assert mock_get.call_args.kwargs["measurement_type"] == "temperature"

    assert mock_get.call_args.kwargs["hive_level_id"] == 2

    assert mock_get.call_args.kwargs["sensor_device_id"] == 10

    # =====================================================
    # FastAPI convertit automatiquement
    # les dates ISO en datetime.
    #
    # On vérifie simplement qu'elles
    # ont bien été transmises.
    # =====================================================
    assert mock_get.call_args.kwargs["start_at"] is not None

    assert mock_get.call_args.kwargs["end_at"] is not None
