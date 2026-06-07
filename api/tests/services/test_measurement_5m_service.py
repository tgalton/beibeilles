from datetime import UTC
from datetime import datetime

from unittest.mock import Mock
from unittest.mock import patch

from app.services import measurement_5m_service


# =========================================================
# Fixture de mesure 5m simulée
#
# Le service retourne normalement des objets SQLAlchemy
# Measurement5m.
#
# Ici un dictionnaire suffit puisque nous mockons
# complètement le repository.
# =========================================================
def fake_measurement() -> dict:

    return {
        "id": 1,
        "type": "temperature",
        "value": 24.5,
        "hive_level_id": 2,
        "sensor_device_id": 10,
        "measured_at": datetime.now(
            UTC,
        ),
    }


# =========================================================
# Vérifie que le service retourne bien
# le résultat fourni par le repository.
# =========================================================
@patch(
    "app.repositories.measurement_5m_repository.get_all",
)
def test_get_measurements_5m(
    mock_get_all: Mock,
) -> None:

    measurements = [
        fake_measurement(),
    ]

    mock_get_all.return_value = measurements

    result = measurement_5m_service.get_measurements_5m(
        db=Mock(),
    )

    assert result == measurements


# =========================================================
# Vérifie que tous les filtres sont correctement
# transmis au repository.
#
# C'est important :
# le service ne doit pas perdre ou modifier
# les paramètres reçus.
# =========================================================
@patch(
    "app.repositories.measurement_5m_repository.get_all",
)
def test_get_measurements_5m_passes_filters(
    mock_get_all: Mock,
) -> None:

    start_at = datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    )

    end_at = datetime(
        2026,
        1,
        2,
        tzinfo=UTC,
    )

    measurement_5m_service.get_measurements_5m(
        db=Mock(),
        measurement_type="temperature",
        hive_level_id=5,
        sensor_device_id=9,
        start_at=start_at,
        end_at=end_at,
    )

    mock_get_all.assert_called_once()

    assert (
        mock_get_all.call_args.kwargs["measurement_type"]
        == "temperature"
    )

    assert (
        mock_get_all.call_args.kwargs["hive_level_id"]
        == 5
    )

    assert (
        mock_get_all.call_args.kwargs["sensor_device_id"]
        == 9
    )

    assert (
        mock_get_all.call_args.kwargs["start_at"]
        == start_at
    )

    assert (
        mock_get_all.call_args.kwargs["end_at"]
        == end_at
    )