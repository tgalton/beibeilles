from app.models.measurement_5m import (
    Measurement5m,
)


# =========================================================
# PARAMETRES ALGORITHME V1
#
# IMPORTANT :
#
# Ces constantes sont volontairement
# centralisées afin de pouvoir être
# ajustées facilement lors des essais
# terrain.
# =========================================================

MAX_BUCKET_VARIATION_KG = 0.050

MIN_STABLE_BUCKET_COUNT = 6


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

    variation = (
        measurement.max_value
        - measurement.min_value
    )

    return (
        variation
        <= MAX_BUCKET_VARIATION_KG
    )


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
        for measurement
        in measurements
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

    if (
        len(measurements)
        < MIN_STABLE_BUCKET_COUNT
    ):
        return False

    return (
        count_stable_buckets(
            measurements,
        )
        == len(measurements)
    )

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

    return (
        sum(
            measurement.avg_value
            for measurement
            in measurements
        )
        / len(measurements)
    )