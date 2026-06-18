from sqlalchemy.orm import Session

from app.repositories import (
    measurement_5m_repository,
)

from app.repositories import (
    weight_baseline_repository,
)

from app.services import (
    weight_baseline_service,
)

from app.services import (
    auto_recalibration_service,
)

from app.services import (
    measurement_corrected_backfill_service,
)


WINDOW_SIZE = 6


def run(
    db: Session,
    hive_level_id: int,
) -> None:
    """
    =====================================================
    Pipeline complet V1.

    1) récupération des buckets poids

    2) recherche d'une fenêtre stable

    3) création baseline

    4) comparaison avec baseline précédente

    5) création éventuelle d'une calibration
    =====================================================
    """

    measurements = measurement_5m_repository.get_latest_weight_measurements(
        db=db,
        hive_level_id=hive_level_id,
        limit=WINDOW_SIZE,
    )

    print(
        f"[AUTO RECALIBRATION] "
        f"{len(measurements)} measurements found"
    )

    if len(measurements) < WINDOW_SIZE:
        return

    weights = [measurement.avg_value for measurement in measurements]

    timestamps = [float(index * 5) for index in range(len(measurements))]

    print(
        f"[AUTO RECALIBRATION] "
        f"weights={weights}"
    )

    candidate = weight_baseline_service.detect_baseline_candidate(
        hive_level_id=hive_level_id,
        weights=weights,
        timestamps_minutes=timestamps,
    )

    if candidate is None:

        print(
            "[AUTO RECALIBRATION] "
            "no baseline detected"
        )

        return

    current_baseline = weight_baseline_service.save_baseline(
        db=db,
        candidate=candidate,
    )

    reference_baseline = weight_baseline_repository.get_previous_baseline(
        db=db,
        hive_level_id=hive_level_id,
        baseline_id=current_baseline.id,
    )

    if reference_baseline is None:
        return

    proposal = auto_recalibration_service.propose_from_baseline_drift(
        reference_baseline=reference_baseline,
        current_baseline=current_baseline,
    )

    if proposal is None:
        return

    print(
        f"[AUTO RECALIBRATION] "
        f"drift detected "
        f"hive_level={hive_level_id} "
        f"offset={proposal.offset_kg}"
    )

    auto_recalibration_service.create_auto_calibration(
        db=db,
        hive_level_id=hive_level_id,
        proposal=proposal,
    )

    print(
        f"[AUTO RECALIBRATION] "
        f"calibration created "
        f"hive_level={hive_level_id}"
    )

    # =====================================================
    # Une nouvelle calibration modifie potentiellement
    # l'interprétation de tout l'historique.
    #
    # On relance donc immédiatement le calcul
    # des poids corrigés.
    # =====================================================

    measurement_corrected_backfill_service.rebuild_hive_level_history(
        db=db,
        hive_level_id=hive_level_id,
    )

    print(
    f"[AUTO RECALIBRATION] baseline detected "
    f"hive_level={hive_level_id}"
)
