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

# Ce service ne sère pas à faire des batch mais des modification unitaire des mesures via calibration


def create_from_measurement_5m(
    db: Session,
    measurement: Measurement5m,
) -> MeasurementCorrected:
    """
    =====================================================
    Construit puis persiste une mesure corrigée.
    =====================================================
    """

    corrected = build_from_measurement_5m(
        db=db,
        measurement=measurement,
    )

    return measurement_corrected_repository.create(
        db=db,
        measurement=corrected,
    )


def create_or_replace_from_measurement_5m(
    db: Session,
    measurement: Measurement5m,
) -> MeasurementCorrected:
    """
    =====================================================
    Recalcule une mesure corrigée.

    Si une ligne existe déjà :

        UPDATE

    Sinon :

        CREATE

    Cette méthode est utilisée lors
    des recalculs historiques.
    =====================================================
    """

    if measurement.hive_level_id is None:
        raise ValueError(
            "Measurement must have hive_level_id",
        )

    corrected_weight = weight_calibration_service.apply_calibration(
        db=db,
        hive_level_id=measurement.hive_level_id,
        raw_weight=measurement.avg_value,
        measured_at=measurement.bucket_at,
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

    existing = measurement_corrected_repository.get_by_measurement_5m_id(
        db=db,
        measurement_5m_id=measurement.id,
    )

    if existing is None:
        corrected = MeasurementCorrected(
            measurement_5m_id=measurement.id,
            calibration_id=calibration.id,
            raw_weight_kg=measurement.avg_value,
            corrected_weight_kg=corrected_weight,
        )

        return measurement_corrected_repository.create(
            db=db,
            measurement=corrected,
        )

    existing.calibration_id = calibration.id

    existing.raw_weight_kg = measurement.avg_value

    existing.corrected_weight_kg = corrected_weight

    return measurement_corrected_repository.update(
        db=db,
        measurement=existing,
    )


def build_from_measurement_5m(
    db: Session,
    measurement: Measurement5m,
) -> MeasurementCorrected:
    """
    =====================================================
    Construit une mesure corrigée.

    Ne persiste rien.

    Utilisé par :

    - backfill historique
    - recalcul massif
    - migration d'algorithme
    =====================================================
    """

    if measurement.hive_level_id is None:
        raise ValueError(
            "Measurement must have hive_level_id",
        )

    calibration = weight_calibration_service.get_calibration_for_datetime(
        db=db,
        hive_level_id=measurement.hive_level_id,
        measured_at=measurement.bucket_at,
    )

    if calibration is None:
        corrected_weight = measurement.avg_value

        calibration_id = None

    else:
        corrected_weight = weight_calibration_service.apply_calibration(
            db=db,
            hive_level_id=measurement.hive_level_id,
            raw_weight=measurement.avg_value,
            measured_at=measurement.bucket_at,
        )

        calibration_id = calibration.id

    return MeasurementCorrected(
        measurement_5m_id=measurement.id,
        calibration_id=calibration_id,
        raw_weight_kg=measurement.avg_value,
        corrected_weight_kg=corrected_weight,
    )
