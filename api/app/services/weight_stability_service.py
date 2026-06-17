from statistics import variance

from app.dto.stability_analysis_dto import (
    StabilityAnalysisDTO,
)


# =========================================================
# PARAMETRES CENTRALISES
# =========================================================

MAX_VARIANCE_KG = 0.05

MAX_SLOPE_KG_PER_HOUR = 0.20

MIN_DURATION_MINUTES = 30


def analyze_stability(
    weights: list[float],
    timestamps_minutes: list[float],
) -> StabilityAnalysisDTO:
    """
    =====================================================
    Analyse une période de mesures.
    =====================================================

    Une période est considérée stable si :

    - variance faible
    - pente faible
    - durée suffisante

    La pente est calculée par régression
    linéaire.
    =====================================================
    """

    if len(weights) < 2:
        raise ValueError(
            "At least two measurements required",
        )

    if len(weights) != len(
        timestamps_minutes,
    ):
        raise ValueError(
            "weights and timestamps length mismatch",
        )

    variance_value = compute_variance(
        weights,
    )

    slope = compute_linear_slope(
        timestamps_minutes,
        weights,
    )

    duration_minutes = int(max(timestamps_minutes) - min(timestamps_minutes))

    confidence = compute_confidence(
        standard_deviation_kg=variance_value,
        slope_kg_per_hour=abs(slope),
        duration_minutes=duration_minutes,
    )

    is_stable = (
        variance_value <= MAX_VARIANCE_KG
        and abs(slope) <= MAX_SLOPE_KG_PER_HOUR
        and duration_minutes >= MIN_DURATION_MINUTES
    )

    return StabilityAnalysisDTO(
        standard_deviation_kg=variance_value,
        slope_kg_per_hour=slope,
        duration_minutes=duration_minutes,
        confidence=confidence,
        is_stable=is_stable,
    )


def compute_variance(
    weights: list[float],
) -> float:
    """
    =====================================================
    Variance statistique simple.
    =====================================================
    """

    if len(weights) < 2:
        return 0.0

    return float(
        variance(weights),
    )


def compute_linear_slope(
    x_values: list[float],
    y_values: list[float],
) -> float:
    """
    =====================================================
    Régression linéaire simple.

    Retour :

        kg / heure

    Exemple :

        +0.1 kg en 1h

    => pente = 0.1
    =====================================================
    """

    n = len(x_values)

    mean_x = sum(x_values) / n

    mean_y = sum(y_values) / n

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in zip(
            x_values,
            y_values,
            strict=False,
        )
    )

    denominator = sum((x - mean_x) ** 2 for x in x_values)

    if denominator == 0:
        return 0.0

    slope_per_minute = numerator / denominator

    return slope_per_minute * 60


def compute_confidence(
    standard_deviation_kg: float,
    slope_kg_per_hour: float,
    duration_minutes: int,
) -> float:
    """
    =====================================================
    Score de confiance.

    V1 simple.

    0 -> très mauvais

    1 -> très bon
    =====================================================
    """

    variance_score = max(
        0.0,
        1.0 - (standard_deviation_kg / MAX_VARIANCE_KG),
    )

    slope_score = max(
        0.0,
        1.0 - (slope_kg_per_hour / MAX_SLOPE_KG_PER_HOUR),
    )

    duration_score = min(
        1.0,
        duration_minutes / MIN_DURATION_MINUTES,
    )

    return round(
        (variance_score + slope_score + duration_score) / 3,
        4,
    )
