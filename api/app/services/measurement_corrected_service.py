from sqlalchemy.orm import Session

from app.models.measurement_5m import (
    Measurement5m,
)

from app.models.measurement_corrected import (
    MeasurementCorrected,
)

from app.repositories import (
    measurement_corrected_repository,
)

from app.services import (
    weight_calibration_service,
)


def create_corrected_measurement(
    db: Session,
    measurement: Measurement5m,
) -> MeasurementCorrected:
    """
    =====================================================
    Applique la calibration valide
    à la date du bucket.

    Puis persiste le résultat.

    IMPORTANT :

    La calibration utilisée est celle
    valide au moment de la mesure.

    Cela garantit qu'un recalcul
    historique reste cohérent.
    =====================================================
    """

    corrected_weight = (
        weight_calibration_service
        .apply_calibration(
            db=db,
            hive_level_id=measurement.hive_level_id,
            raw_weight=measurement.avg_value,
            measured_at=measurement.bucket_at,
        )
    )

    calibration = (
        weight_calibration_service
        .get_calibration_for_datetime(
            db=db,
            hive_level_id=measurement.hive_level_id,
            measured_at=measurement.bucket_at,
        )
    )

    if calibration is None:
        raise ValueError(
            "No calibration found",
        )

    corrected = MeasurementCorrected(
        measurement_5m_id=measurement.id,
        calibration_id=calibration.id,
        raw_weight_kg=measurement.avg_value,
        corrected_weight_kg=corrected_weight,
    )

    return (
        measurement_corrected_repository
        .create(
            db=db,
            measurement=corrected,
        )
    )


