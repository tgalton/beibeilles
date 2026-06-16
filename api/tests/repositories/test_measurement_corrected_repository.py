from datetime import UTC
from datetime import datetime

from app.models.measurement_corrected import (
    MeasurementCorrected,
)
from app.repositories import (
    measurement_corrected_repository,
)


def test_create_measurement_corrected(
    db_session,
):
    """
    =====================================================
    Vérifie la persistance.
    =====================================================
    """

    measurement = MeasurementCorrected(
        measurement_5m_id=1,
        hive_level_id=1,
        measured_at=datetime.now(UTC),
        raw_value=50.0,
        corrected_value=49.8,
        calibration_id=None,
    )

    result = (
        measurement_corrected_repository
        .create(
            db=db_session,
            measurement=measurement,
        )
    )

    assert result.id is not None


def test_get_by_measurement_5m_id(
    db_session,
):
    """
    =====================================================
    Vérifie la recherche par mesure source.
    =====================================================
    """

    measurement = MeasurementCorrected(
        measurement_5m_id=123,
        hive_level_id=1,
        measured_at=datetime.now(UTC),
        raw_value=50.0,
        corrected_value=49.8,
    )

    (
        measurement_corrected_repository
        .create(
            db=db_session,
            measurement=measurement,
        )
    )

    result = (
        measurement_corrected_repository
        .get_by_measurement_5m_id(
            db=db_session,
            measurement_5m_id=123,
        )
    )

    assert result is not None

    assert result.corrected_value == 49.8