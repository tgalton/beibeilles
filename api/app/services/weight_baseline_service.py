from datetime import UTC
from datetime import datetime

from app.models.measurement_5m import Measurement5m
from app.dto.baseline_candidate_dto import (
    BaselineCandidateDTO,
)
from app.models.weight_baseline import (
    WeightBaseline,
)

from app.services import (
    weight_stability_service,
)

from sqlalchemy.orm import Session

from app.repositories import (
    weight_baseline_repository,
)

# =========================================================
# VERSION ALGORITHME
#
# Permet de tracer précisément
# quelle logique a produit une baseline.
# =========================================================

ALGORITHM_VERSION = "v1"

MAX_BUCKET_VARIATION_KG = 0.050

MIN_STABLE_BUCKET_COUNT = 6


def save_baseline(
    db: Session,
    candidate: BaselineCandidateDTO,
) -> WeightBaseline:
    """
    =====================================================
    Persiste une baseline calculée.
    =====================================================
    """

    baseline = build_baseline(
        candidate,
    )

    return weight_baseline_repository.create(
        db=db,
        baseline=baseline,
    )


def is_bucket_stable(
    measurement: Measurement5m,
) -> bool:
    """
    =====================================================
    Vérifie qu'un bucket individuel est stable.
    =====================================================

    Critère V1 :

    max_value - min_value

    Exemple :

    min = 52.121
    max = 52.125

    variation = 0.004 kg

    => stable
    =====================================================
    """

    variation = measurement.max_value - measurement.min_value

    return variation <= MAX_BUCKET_VARIATION_KG


def count_stable_buckets(
    measurements: list[Measurement5m],
) -> int:
    """
    =====================================================
    Compte le nombre de buckets stables.
    =====================================================
    """

    return sum(
        1
        for measurement in measurements
        if is_bucket_stable(
            measurement,
        )
    )


def is_stable_window(
    measurements: list[Measurement5m],
) -> bool:
    """
    =====================================================
    Vérifie si une fenêtre complète
    peut être considérée comme stable.

    V1 :

    Tous les buckets doivent être stables.

    Exemple :

    6 buckets
    × 5 minutes

    = 30 minutes de stabilité
    =====================================================
    """

    if len(measurements) < MIN_STABLE_BUCKET_COUNT:
        return False

    return count_stable_buckets(
        measurements,
    ) == len(measurements)


def compute_baseline_weight(
    measurements: list[Measurement5m],
) -> float:
    """
    =====================================================
    Calcule le poids moyen observé
    sur une fenêtre stable.

    Cette valeur servira plus tard
    à créer un WeightBaseline.
    =====================================================
    """

    if not measurements:
        raise ValueError(
            "measurements cannot be empty",
        )

    return sum(measurement.avg_value for measurement in measurements) / len(
        measurements
    )


def detect_baseline_candidate(
    hive_level_id: int,
    weights: list[float],
    timestamps_minutes: list[float],
) -> BaselineCandidateDTO | None:
    """
    =====================================================
    Analyse une fenêtre de mesures.

    Si la fenêtre est suffisamment stable :

        -> retourne un candidat baseline

    Sinon :

        -> retourne None

    IMPORTANT :

    Cette fonction ne persiste rien.

    Elle ne fait qu'évaluer
    la qualité d'une fenêtre.
    =====================================================
    """

    analysis = weight_stability_service.analyze_stability(
        weights=weights,
        timestamps_minutes=timestamps_minutes,
    )

    if not analysis.is_stable:
        return None

    baseline_weight = sum(weights) / len(weights)

    return BaselineCandidateDTO(
        hive_level_id=hive_level_id,
        baseline_offset_kg=baseline_weight,
        confidence=analysis.confidence,
        stable_duration_minutes=(max(timestamps_minutes) - min(timestamps_minutes)),
        algorithm_version=ALGORITHM_VERSION,
    )


def build_baseline(
    candidate: BaselineCandidateDTO,
) -> WeightBaseline:
    """
    =====================================================
    Transforme un candidat baseline
    en modèle SQLAlchemy persistant.
    =====================================================
    """

    return WeightBaseline(
        hive_level_id=(candidate.hive_level_id),
        computed_at=datetime.now(UTC),
        baseline_offset_kg=(candidate.baseline_offset_kg),
        confidence=(candidate.confidence),
        stable_duration_minutes=(candidate.stable_duration_minutes),
        algorithm_version=(candidate.algorithm_version),
    )
