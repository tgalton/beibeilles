"""
=========================================================
Tests du moteur de calibration des balances
=========================================================

Ce service est critique pour la qualité des mesures
de poids.

Son rôle n'est PAS de modifier les mesures stockées.

Il doit uniquement :

- retrouver la calibration active
- calculer un poids corrigé
- appliquer offset et gain

Formule métier :

poids_corrige =
(poids_brut - offset)
× gain

Exemple :

poids brut : 50 kg

offset : -2 kg

gain : 1.05

=>

poids corrigé :

(50 - (-2))
× 1.05

=
54.6 kg

IMPORTANT :

Les données RAW restent toujours intactes.

Toutes les corrections sont calculées
dynamiquement.
=========================================================
"""

from datetime import UTC
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

from app.enums.calibration_source import CalibrationSource
from app.models.weight_calibration import WeightCalibration

from app.services import weight_calibration_service


# calibration active trouvée
@patch("app.services.weight_calibration_service.weight_calibration_repository")
def test_get_current_calibration_found(
    mock_repository,
):
    calibration = WeightCalibration(
        id=1,
        hive_level_id=1,
        valid_from=datetime.now(UTC),
        valid_to=None,
        offset_kg=-2.0,
        gain=1.0,
        source=CalibrationSource.AUTO_DRIFT,
    )

    mock_repository.get_current_for_hive_level.return_value = calibration

    db = Mock()

    result = weight_calibration_service.get_current_calibration(
        db=db,
        hive_level_id=1,
    )

    assert result == calibration


# aucune calibration
@patch("app.services.weight_calibration_service.weight_calibration_repository")
def test_get_current_calibration_none(
    mock_repository,
):
    """
    =====================================================
    Si aucune calibration n'existe
    on doit retourner None.
    =====================================================
    """

    mock_repository.get_current_for_hive_level.return_value = None

    db = Mock()

    result = weight_calibration_service.get_current_calibration(
        db=db,
        hive_level_id=1,
    )

    assert result is None


# poids brut sans calibration
@patch("app.services.weight_calibration_service.weight_calibration_repository")
def test_apply_calibration_without_calibration(
    mock_repository,
):
    """
    =====================================================
    Sans calibration active
    aucune correction ne doit être appliquée.
    =====================================================
    """

    mock_repository.get_for_datetime.return_value = None

    db = Mock()

    result = weight_calibration_service.apply_calibration(
        db=db,
        hive_level_id=1,
        raw_weight=50.0,
        measured_at=datetime.now(UTC),
    )

    assert result == 50.0


# offset seul
@patch("app.services.weight_calibration_service.weight_calibration_repository")
def test_apply_calibration_offset_only(
    mock_repository,
):
    """
    =====================================================
    Vérifie le calcul :

    poids_corrige =
    poids_brut - offset
    =====================================================
    """

    calibration = WeightCalibration(
        id=1,
        hive_level_id=1,
        valid_from=datetime.now(UTC),
        valid_to=None,
        offset_kg=-2.0,
        gain=1.0,
        source=CalibrationSource.AUTO_DRIFT,
    )

    mock_repository.get_for_datetime.return_value = calibration

    db = Mock()

    result = weight_calibration_service.apply_calibration(
        db=db,
        hive_level_id=1,
        raw_weight=50.0,
        measured_at=datetime.now(UTC),
    )

    assert result == 52.0


# offset + gain
@patch("app.services.weight_calibration_service.weight_calibration_repository")
def test_apply_calibration_offset_and_gain(
    mock_repository,
):
    """
    =====================================================
    Vérifie la formule complète :

    (poids - offset) × gain
    =====================================================
    """

    calibration = WeightCalibration(
        id=1,
        hive_level_id=1,
        valid_from=datetime.now(UTC),
        valid_to=None,
        offset_kg=-2.0,
        gain=1.05,
        source=CalibrationSource.REFERENCE_WEIGHT,
    )

    mock_repository.get_for_datetime.return_value = calibration

    db = Mock()

    result = weight_calibration_service.apply_calibration(
        db=db,
        hive_level_id=1,
        raw_weight=50.0,
        measured_at=datetime.now(UTC),
    )

    assert result == 54.6


# gain inférieur à 1
@patch("app.services.weight_calibration_service.weight_calibration_repository")
def test_apply_calibration_gain_less_than_one(
    mock_repository,
):
    """
    =====================================================
    Certaines balances surestiment le poids.

    Le gain peut alors être inférieur à 1.
    =====================================================
    """

    calibration = WeightCalibration(
        id=1,
        hive_level_id=1,
        valid_from=datetime.now(UTC),
        valid_to=None,
        offset_kg=0.0,
        gain=0.95,
        source=CalibrationSource.REFERENCE_WEIGHT,
    )

    mock_repository.get_for_datetime.return_value = calibration

    db = Mock()

    result = weight_calibration_service.apply_calibration(
        db=db,
        hive_level_id=1,
        raw_weight=100.0,
        measured_at=datetime.now(UTC),
    )

    assert result == 95.0
