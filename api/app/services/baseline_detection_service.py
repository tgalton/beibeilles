from sqlalchemy.orm import Session

from app.models.weight_baseline import (
    WeightBaseline,
)

from app.repositories import (
    measurement_corrected_repository,
)

from app.services import (
    weight_baseline_service,
)


# =========================================================
# PARAMETRES ALGORITHME
# =========================================================
#
# V1 :
#
# Une baseline est recherchée
# sur une fenêtre de :
#
# 6 buckets × 5 min
#
# soit 30 minutes.
# =========================================================

WINDOW_SIZE = 6


def detect_latest_baseline(
    db: Session,
    hive_level_id: int,
) -> WeightBaseline | None:
    """
    =====================================================
    Recherche une fenêtre stable récente.
    =====================================================

    Si la fenêtre est jugée stable :

        -> création d'une baseline

    Sinon :

        -> None
    =====================================================
    """

    measurements = measurement_corrected_repository.get_latest_for_hive_level(
        db=db,
        hive_level_id=hive_level_id,
        limit=WINDOW_SIZE,
    )

    if len(measurements) < WINDOW_SIZE:
        return None

    measurements.reverse()

    weights = [measurement.corrected_weight_kg for measurement in measurements]

    timestamps_minutes = [index * 5 for index in range(len(measurements))]

    candidate = weight_baseline_service.detect_baseline_candidate(
        hive_level_id=hive_level_id,
        weights=weights,
        timestamps_minutes=timestamps_minutes,
    )

    if candidate is None:
        return None

    return weight_baseline_service.save_baseline(
        db=db,
        candidate=candidate,
    )
