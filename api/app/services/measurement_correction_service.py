from app.models.measurement_5m import (
    Measurement5m,
)

from app.models.measurement_corrected import (
    MeasurementCorrected,
)

from app.services import (
    weight_calibration_service,
)

from app.repositories import (
    measurement_corrected_repository,
)


def build_corrected_measurement(
    measurement: Measurement5m,
    corrected_value: float,
    calibration_id: int | None,
) -> MeasurementCorrected:
    """
    =====================================================
    Construit une mesure corrigée.

    Ne persiste rien.
    =====================================================
    """

    return MeasurementCorrected(
        measurement_5m_id=measurement.id,
        hive_level_id=measurement.hive_level_id,
        measured_at=measurement.bucket_at,
        raw_value=measurement.avg_value,
        corrected_value=corrected_value,
        calibration_id=calibration_id,
    )


def create_corrected_measurement(
    db,
    measurement: Measurement5m,
) -> MeasurementCorrected:
    """
    =====================================================
    Applique automatiquement la calibration
    valide à la date de la mesure.
    =====================================================
    """

    calibration = (
        weight_calibration_service
        .get_calibration_for_datetime(
            db=db,
            hive_level_id=measurement.hive_level_id,
            measured_at=measurement.bucket_at,
        )
    )

    if calibration is None:

        corrected_value = measurement.avg_value

        calibration_id = None

    else:

        corrected_value = (
            (
                measurement.avg_value
                - calibration.offset_kg
            )
            * calibration.gain
        )

        calibration_id = calibration.id

    corrected = (
        build_corrected_measurement(
            measurement=measurement,
            corrected_value=corrected_value,
            calibration_id=calibration_id,
        )
    )

    return (
        measurement_corrected_repository
        .create(
            db=db,
            measurement=corrected,
        )
    )