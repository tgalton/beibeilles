from unittest.mock import Mock
from unittest.mock import patch

from app.models.weight_reference_event import (
    WeightReferenceEvent,
)

from app.services import (
    weight_reference_service,
)


# =====================================================
# Création d'un événement de référence
# =====================================================
@patch(
    "app.services.weight_reference_service."
    "weight_reference_event_repository"
)
def test_create_reference_event(
    mock_repository,
):
    """
    =====================================================
    Vérifie qu'un événement de référence
    est correctement construit puis persisté.
    =====================================================
    """

    created_event = WeightReferenceEvent(
        id=1,
        hive_level_id=1,
        expected_delta_kg=1.0,
        measured_delta_kg=0.95,
    )

    mock_repository.create.return_value = (
        created_event
    )

    db = Mock()

    result = (
        weight_reference_service
        .create_reference_event(
            db=db,
            hive_level_id=1,
            expected_delta_kg=1.0,
            measured_delta_kg=0.95,
            comment="Poids étalon 1kg",
        )
    )

    assert result == created_event

    mock_repository.create.assert_called_once()


# =====================================================
# Calcul d'un gain > 1
# =====================================================
def test_compute_gain_from_reference_gain_above_one():
    """
    =====================================================
    Exemple :

    poids attendu : 1.00 kg
    poids mesuré  : 0.95 kg

    La balance sous-estime.

    Le gain doit être supérieur à 1.
    =====================================================
    """

    gain = (
        weight_reference_service
        .compute_gain_from_reference(
            expected_delta_kg=1.0,
            measured_delta_kg=0.95,
        )
    )

    assert round(gain, 6) == round(
        1.0 / 0.95,
        6,
    )


# =====================================================
# Calcul d'un gain < 1
# =====================================================
def test_compute_gain_from_reference_gain_below_one():
    """
    =====================================================
    Exemple :

    poids attendu : 1.00 kg
    poids mesuré  : 1.05 kg

    La balance surestime.

    Le gain doit être inférieur à 1.
    =====================================================
    """

    gain = (
        weight_reference_service
        .compute_gain_from_reference(
            expected_delta_kg=1.0,
            measured_delta_kg=1.05,
        )
    )

    assert round(gain, 6) == round(
        1.0 / 1.05,
        6,
    )


# =====================================================
# Cas parfait
# =====================================================
def test_compute_gain_from_reference_perfect():
    """
    =====================================================
    Si la mesure est parfaite :

    attendu = mesuré

    alors le gain doit être exactement 1.
    =====================================================
    """

    gain = (
        weight_reference_service
        .compute_gain_from_reference(
            expected_delta_kg=1.0,
            measured_delta_kg=1.0,
        )
    )

    assert gain == 1.0


# =====================================================
# Sécurité division par zéro
# =====================================================
def test_compute_gain_from_reference_zero_measurement():
    """
    =====================================================
    Une mesure de référence à zéro
    rend le calcul impossible.

    Une exception doit être levée.
    =====================================================
    """

    try:

        (
            weight_reference_service
            .compute_gain_from_reference(
                expected_delta_kg=1.0,
                measured_delta_kg=0.0,
            )
        )

        assert False

    except ValueError:

        assert True


# =====================================================
# Dernier événement disponible
# =====================================================
@patch(
    "app.services.weight_reference_service."
    "weight_reference_event_repository"
)
def test_get_latest_reference_event_found(
    mock_repository,
):
    """
    =====================================================
    Vérifie qu'on retourne correctement
    le dernier événement de référence.
    =====================================================
    """

    event = WeightReferenceEvent(
        id=1,
        hive_level_id=1,
        expected_delta_kg=1.0,
        measured_delta_kg=0.97,
    )

    mock_repository.get_latest_for_hive_level.return_value = (
        event
    )

    db = Mock()

    result = (
        weight_reference_service
        .get_latest_reference_event(
            db=db,
            hive_level_id=1,
        )
    )

    assert result == event


# =====================================================
# Aucun événement disponible
# =====================================================
@patch(
    "app.services.weight_reference_service."
    "weight_reference_event_repository"
)
def test_get_latest_reference_event_none(
    mock_repository,
):
    """
    =====================================================
    Si aucun événement n'existe
    on doit retourner None.
    =====================================================
    """

    mock_repository.get_latest_for_hive_level.return_value = (
        None
    )

    db = Mock()

    result = (
        weight_reference_service
        .get_latest_reference_event(
            db=db,
            hive_level_id=1,
        )
    )

    assert result is None