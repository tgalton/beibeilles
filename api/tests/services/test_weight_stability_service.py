from app.services import (
    weight_stability_service,
)
import pytest


def test_compute_variance_flat():
    """
    =====================================================
    Toutes les valeurs sont identiques.

    La variance doit être nulle.
    =====================================================
    """

    result = weight_stability_service.compute_variance(
        [
            50.0,
            50.0,
            50.0,
            50.0,
        ]
    )

    assert result == 0.0


def test_compute_variance_non_zero():
    """
    =====================================================
    Une dispersion doit produire
    une variance strictement positive.
    =====================================================
    """

    result = weight_stability_service.compute_variance(
        [
            50.0,
            51.0,
            49.0,
            52.0,
        ]
    )

    assert result > 0


def test_compute_linear_slope_flat():
    """
    =====================================================
    Courbe parfaitement plate.

    Pente attendue : 0
    =====================================================
    """

    result = weight_stability_service.compute_linear_slope(
        x_values=[
            0,
            10,
            20,
            30,
        ],
        y_values=[
            50,
            50,
            50,
            50,
        ],
    )

    assert round(result, 6) == 0


def test_compute_linear_slope_positive():
    """
    =====================================================
    Le poids augmente.

    La pente doit être positive.
    =====================================================
    """

    result = weight_stability_service.compute_linear_slope(
        x_values=[
            0,
            10,
            20,
            30,
        ],
        y_values=[
            50,
            51,
            52,
            53,
        ],
    )

    assert result > 0


def test_compute_linear_slope_negative():
    """
    =====================================================
    Le poids diminue.

    La pente doit être négative.
    =====================================================
    """

    result = weight_stability_service.compute_linear_slope(
        x_values=[
            0,
            10,
            20,
            30,
        ],
        y_values=[
            53,
            52,
            51,
            50,
        ],
    )

    assert result < 0


def test_compute_linear_slope_single_x():
    """
    =====================================================
    Protection contre une division
    par zéro.

    Tous les x sont identiques.
    =====================================================
    """

    result = weight_stability_service.compute_linear_slope(
        x_values=[
            0,
            0,
            0,
        ],
        y_values=[
            50,
            51,
            52,
        ],
    )

    assert result == 0.0


def test_compute_confidence_perfect():
    """
    =====================================================
    Cas idéal.

    Variance nulle.
    Pente nulle.
    Durée suffisante.
    =====================================================
    """

    result = weight_stability_service.compute_confidence(
        standard_deviation_kg=0,
        slope_kg_per_hour=0,
        duration_minutes=60,
    )

    assert result == 1.0


def test_compute_confidence_bad():
    """
    =====================================================
    Cas très mauvais.

    La confiance doit être faible.
    =====================================================
    """

    result = weight_stability_service.compute_confidence(
        standard_deviation_kg=100,
        slope_kg_per_hour=100,
        duration_minutes=1,
    )

    assert result < 0.1


def test_analyze_stability_stable():
    """
    =====================================================
    Fenêtre très stable.

    Le système doit la considérer
    comme exploitable.
    =====================================================
    """

    result = weight_stability_service.analyze_stability(
        weights=[
            50.00,
            50.01,
            49.99,
            50.00,
            50.01,
        ],
        timestamps_minutes=[
            0,
            10,
            20,
            30,
            40,
        ],
    )

    assert result.is_stable is True

    assert result.confidence > 0.8


def test_analyze_stability_unstable_variance():
    """
    =====================================================
    Variance énorme.

    Doit être rejetée.
    =====================================================
    """

    result = weight_stability_service.analyze_stability(
        weights=[
            50,
            60,
            40,
            58,
            42,
        ],
        timestamps_minutes=[
            0,
            10,
            20,
            30,
            40,
        ],
    )

    assert result.is_stable is False


def test_analyze_stability_unstable_slope():
    """
    =====================================================
    Dérive continue.

    La pente doit provoquer
    un rejet.
    =====================================================
    """

    result = weight_stability_service.analyze_stability(
        weights=[
            50,
            51,
            52,
            53,
            54,
        ],
        timestamps_minutes=[
            0,
            10,
            20,
            30,
            40,
        ],
    )

    assert result.is_stable is False


def test_analyze_stability_not_enough_points():
    """
    =====================================================
    Il faut au minimum deux mesures.
    =====================================================
    """

    with pytest.raises(
        ValueError,
    ):
        (
            weight_stability_service.analyze_stability(
                weights=[
                    50,
                ],
                timestamps_minutes=[
                    0,
                ],
            )
        )
