from sqlalchemy.orm import Session

from app.models.weight_baseline import (
    WeightBaseline,
)


def create(
    db: Session,
    baseline: WeightBaseline,
) -> WeightBaseline:
    """
    =====================================================
    Persiste une baseline.
    =====================================================
    """

    db.add(baseline)

    db.commit()

    db.refresh(baseline)

    return baseline


def get_by_id(
    db: Session,
    baseline_id: int,
) -> WeightBaseline | None:
    """
    =====================================================
    Recherche une baseline par identifiant.
    =====================================================
    """

    return (
        db.query(WeightBaseline)
        .filter(
            WeightBaseline.id == baseline_id,
        )
        .first()
    )


def get_latest_for_hive_level(
    db: Session,
    hive_level_id: int,
) -> WeightBaseline | None:
    """
    =====================================================
    Retourne la baseline la plus récente.

    IMPORTANT :

    Une baseline représente une estimation
    ponctuelle produite par l'algorithme.

    Plusieurs baselines peuvent donc exister
    dans l'historique d'une même balance.
    =====================================================
    """

    return (
        db.query(WeightBaseline)
        .filter(
            WeightBaseline.hive_level_id == hive_level_id,
        )
        .order_by(
            WeightBaseline.computed_at.desc(),
        )
        .first()
    )


def get_recent_for_hive_level(
    db: Session,
    hive_level_id: int,
    limit: int = 20,
) -> list[WeightBaseline]:
    """
    =====================================================
    Retourne les dernières baselines.

    Utilisé pour :

    - visualisation dashboard
    - suivi de dérive
    - analyse statistique
    =====================================================
    """

    return (
        db.query(WeightBaseline)
        .filter(
            WeightBaseline.hive_level_id == hive_level_id,
        )
        .order_by(
            WeightBaseline.computed_at.desc(),
        )
        .limit(limit)
        .all()
    )


def get_previous_baseline(
    db: Session,
    hive_level_id: int,
    baseline_id: int,
) -> WeightBaseline | None:
    """
    =====================================================
    Baseline précédente.
    =====================================================
    """

    return (
        db.query(
            WeightBaseline,
        )
        .filter(
            WeightBaseline.hive_level_id == hive_level_id,
        )
        .filter(
            WeightBaseline.id < baseline_id,
        )
        .order_by(
            WeightBaseline.id.desc(),
        )
        .first()
    )
