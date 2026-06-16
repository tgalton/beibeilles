from sqlalchemy.orm import Session

from app.models.weight_calibration import (
    WeightCalibration,
)
from app.services import (
    auto_recalibration_service,
)
from app.services import (
    weight_baseline_service,
)


# =========================================================
# PIPELINE DE RECALIBRATION AUTOMATIQUE
# =========================================================
#
# Ce service orchestre l'ensemble du workflow :
#
# mesures
# -> baseline
# -> proposition
# -> calibration
#
# Il ne contient aucun calcul métier.
#
# Son rôle est uniquement
# d'enchaîner les services spécialisés.
# =========================================================


def process_stable_window(
    db: Session,
    hive_level_id: int,
    reference_baseline,
    weights: list[float],
    timestamps_minutes: list[float],
) -> WeightCalibration | None:
    """
    =====================================================
    Analyse une fenêtre stable potentielle.
    =====================================================

    Retour :

        WeightCalibration créée

    ou :

        None
    =====================================================
    """

    candidate = (
        weight_baseline_service
        .detect_baseline_candidate(
            hive_level_id=hive_level_id,
            weights=weights,
            timestamps_minutes=timestamps_minutes,
        )
    )

    if candidate is None:
        return None

    current_baseline = (
        weight_baseline_service
        .build_baseline(
            candidate=candidate,
        )
    )

    proposal = (
        auto_recalibration_service
        .propose_from_baseline_drift(
            reference_baseline=reference_baseline,
            current_baseline=current_baseline,
        )
    )

    if proposal is None:
        return None

    return (
        auto_recalibration_service
        .create_auto_calibration(
            db=db,
            hive_level_id=hive_level_id,
            proposal=proposal,
        )
    )