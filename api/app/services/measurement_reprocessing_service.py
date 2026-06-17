from sqlalchemy.orm import Session


from app.services import (
    measurement_corrected_service,
)

from app.repositories import (
    measurement_5m_repository,
)


def rebuild_corrected_measurements(
    db: Session,
    hive_level_id: int,
) -> int:
    """
    =====================================================
    Recalcule tous les poids corrigés
    d'un niveau de ruche.

    IMPORTANT :

    Les poids bruts restent inchangés.

    Les MeasurementCorrected sont
    reconstruits à partir :

        Measurement5m
            +
        WeightCalibration

    Retour :

        nombre de mesures recalculées
    =====================================================
    """

    measurements = measurement_5m_repository.get_weight_measurements_for_hive_level(
        db=db,
        hive_level_id=hive_level_id,
    )

    count = 0

    for measurement in measurements:
        measurement_corrected_service.create_or_replace_from_measurement_5m(
            db=db,
            measurement=measurement,
        )

        count += 1

    return count
