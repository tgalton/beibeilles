from sqlalchemy.orm import Session

from app.models.weight_calibration import (
    WeightCalibration,
)

from app.repositories import (
    measurement_5m_repository,
)

from app.services import (
    measurement_corrected_service,
)

from app.repositories import (
    measurement_corrected_repository,
)


def backfill_from_calibration(
    db: Session,
    calibration: WeightCalibration,
) -> int:
    """
    =====================================================
    Recalcule toutes les mesures impactées
    par une calibration.

    Retour :

        nombre de mesures recalculées
    =====================================================
    """

    measurements = measurement_5m_repository.get_between_dates(
        db=db,
        hive_level_id=calibration.hive_level_id,
        start_at=calibration.valid_from,
        end_at=(calibration.valid_to or calibration.valid_from),
    )

    count = 0

    for measurement in measurements:
        measurement_corrected_service.create_from_measurement_5m(
            db=db,
            measurement=measurement,
        )

        count += 1

    return count


def rebuild_hive_level_history(
    db: Session,
    hive_level_id: int,
) -> int:
    """
    =====================================================
    Recalcule tout l'historique corrigé.

    Utilisé :

    - après recalibration
    - migration algorithme
    - correction manuelle
    =====================================================
    """

    measurements = measurement_5m_repository.get_weight_measurements_for_hive_level(
        db=db,
        hive_level_id=hive_level_id,
    )

    count = 0

    for measurement in measurements:
        corrected = measurement_corrected_service.build_from_measurement_5m(
            db=db,
            measurement=measurement,
        )

        measurement_corrected_repository.upsert(
            db=db,
            measurement=corrected,
        )

        count += 1

    return count
