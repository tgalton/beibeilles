from unittest.mock import Mock

from app.dto.baseline_candidate_dto import (
    BaselineCandidateDTO,
)
from app.services import (
    weight_baseline_service,
)


# =====================================================
# Helpers
# =====================================================


def build_measurement(
    min_value: float,
    max_value: float,
    avg_value: float,
):
    """
    =====================================================
    Helper minimal.

    On n'utilise que les attributs réellement
    consommés par le service.
    =====================================================
    """

    measurement = Mock()

    measurement.min_value = min_value
    measurement.max_value = max_value
    measurement.avg_value = avg_value

    return measurement


# =====================================================
# Bucket stable
# =====================================================


def test_is_bucket_stable():
    """
    =====================================================
    Variation :

    50.02 - 50.00

    = 0.02 kg

    inférieur au seuil

    => stable
    =====================================================
    """

    measurement = build_measurement(
        min_value=50.00,
        max_value=50.02,
        avg_value=50.01,
    )

    assert (
        weight_baseline_service.is_bucket_stable(
            measurement,
        )
        is True
    )


# =====================================================
# Bucket instable
# =====================================================


def test_is_bucket_not_stable():
    """
    =====================================================
    Variation :

    50.25 - 50.00

    = 0.25 kg

    supérieur au seuil

    => instable
    =====================================================
    """

    measurement = build_measurement(
        min_value=50.00,
        max_value=50.25,
        avg_value=50.12,
    )

    assert (
        weight_baseline_service.is_bucket_stable(
            measurement,
        )
        is False
    )


# =====================================================
# Comptage des buckets stables
# =====================================================


def test_count_stable_buckets():
    """
    =====================================================
    3 buckets stables

    1 bucket instable

    => résultat attendu : 3
    =====================================================
    """

    measurements = [
        build_measurement(
            50.00,
            50.01,
            50.00,
        ),
        build_measurement(
            50.00,
            50.02,
            50.01,
        ),
        build_measurement(
            50.00,
            50.03,
            50.01,
        ),
        build_measurement(
            50.00,
            50.20,
            50.10,
        ),
    ]

    result = weight_baseline_service.count_stable_buckets(
        measurements,
    )

    assert result == 3


# =====================================================
# Fenêtre stable
# =====================================================


def test_is_stable_window():
    """
    =====================================================
    6 buckets stables

    => fenêtre stable
    =====================================================
    """

    measurements = [
        build_measurement(
            50.00,
            50.01,
            50.00,
        )
        for _ in range(6)
    ]

    assert (
        weight_baseline_service.is_stable_window(
            measurements,
        )
        is True
    )


# =====================================================
# Fenêtre trop courte
# =====================================================


def test_is_stable_window_not_enough_buckets():
    """
    =====================================================
    Seulement 5 buckets

    Le minimum est 6

    => False
    =====================================================
    """

    measurements = [
        build_measurement(
            50.00,
            50.01,
            50.00,
        )
        for _ in range(5)
    ]

    assert (
        weight_baseline_service.is_stable_window(
            measurements,
        )
        is False
    )


# =====================================================
# Fenêtre avec un bucket instable
# =====================================================


def test_is_stable_window_with_unstable_bucket():
    """
    =====================================================
    Un seul bucket instable

    => toute la fenêtre est rejetée
    =====================================================
    """

    measurements = [
        build_measurement(
            50.00,
            50.01,
            50.00,
        )
        for _ in range(5)
    ]

    measurements.append(
        build_measurement(
            50.00,
            50.25,
            50.10,
        )
    )

    assert (
        weight_baseline_service.is_stable_window(
            measurements,
        )
        is False
    )


# =====================================================
# Poids moyen
# =====================================================


def test_compute_baseline_weight():
    """
    =====================================================
    Moyenne :

    (50 + 51 + 52)

    / 3

    = 51
    =====================================================
    """

    measurements = [
        build_measurement(
            50,
            50,
            50,
        ),
        build_measurement(
            51,
            51,
            51,
        ),
        build_measurement(
            52,
            52,
            52,
        ),
    ]

    result = weight_baseline_service.compute_baseline_weight(
        measurements,
    )

    assert result == 51.0


# =====================================================
# Liste vide
# =====================================================


def test_compute_baseline_weight_empty():
    """
    =====================================================
    Une baseline ne peut pas être calculée
    sans données.

    Une exception doit être levée.
    =====================================================
    """

    try:
        (
            weight_baseline_service.compute_baseline_weight(
                [],
            )
        )

        assert False

    except ValueError:
        assert True


def test_detect_baseline_candidate_stable():
    """
    =====================================================
    Une fenêtre stable doit produire
    un candidat baseline.
    =====================================================
    """

    candidate = weight_baseline_service.detect_baseline_candidate(
        hive_level_id=1,
        weights=[
            50.00,
            50.01,
            49.99,
            50.00,
        ],
        timestamps_minutes=[
            0,
            10,
            20,
            30,
        ],
    )

    assert candidate is not None

    assert candidate.hive_level_id == 1


def test_detect_baseline_candidate_unstable():
    """
    =====================================================
    Une fenêtre instable doit être rejetée.
    =====================================================
    """

    candidate = weight_baseline_service.detect_baseline_candidate(
        hive_level_id=1,
        weights=[
            50,
            60,
            40,
            55,
        ],
        timestamps_minutes=[
            0,
            10,
            20,
            30,
        ],
    )

    assert candidate is None


def test_detect_baseline_candidate_mean_weight():
    """
    =====================================================
    Le poids baseline doit être
    la moyenne de la fenêtre.
    =====================================================
    """

    candidate = weight_baseline_service.detect_baseline_candidate(
        hive_level_id=1,
        weights=[
            20.0,
            20.01,
            19.99,
            20.00,
        ],
        timestamps_minutes=[
            0,
            10,
            20,
            30,
        ],
    )

    assert candidate is not None

    assert (
        round(
            candidate.baseline_offset_kg,
            2,
        )
        == 20.00
    )

    assert candidate is not None

    assert candidate.baseline_offset_kg == 20


def test_build_baseline():
    """
    =====================================================
    Vérifie la conversion DTO
    vers modèle SQLAlchemy.
    =====================================================
    """

    candidate = BaselineCandidateDTO(
        hive_level_id=1,
        baseline_offset_kg=50,
        confidence=0.95,
        stable_duration_minutes=30,
        algorithm_version="v1",
    )

    baseline = weight_baseline_service.build_baseline(
        candidate,
    )

    assert baseline.hive_level_id == 1

    assert baseline.confidence == 0.95
