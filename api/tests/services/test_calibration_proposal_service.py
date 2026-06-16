from app.services import (
    calibration_proposal_service,
)
from pytest import approx

def test_propose_from_reference_event():
    """
    =====================================================
    Vérifie le calcul du gain.
    =====================================================
    """

    proposal = (
        calibration_proposal_service
        .propose_from_reference_event(
            expected_delta_kg=1.0,
            measured_delta_kg=0.95,
        )
    )

    assert round(
        proposal.gain,
        4,
    ) == round(
        1 / 0.95,
        4,
    )

    assert proposal.offset_kg == approx(0.0)


def test_propose_from_baseline_drift():
    """
    =====================================================
    Vérifie le calcul d'offset.
    =====================================================
    """

    proposal = (
        calibration_proposal_service
        .propose_from_baseline_drift(
            baseline_weight=50.0,
            current_weight=51.2,
        )
    )

    assert proposal.offset_kg == approx(1.2)

    assert proposal.gain == approx(1.0)