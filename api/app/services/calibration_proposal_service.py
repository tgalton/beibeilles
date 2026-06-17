from app.dto.calibration_proposal_dto import (
    CalibrationProposalDTO,
)
from app.enums.calibration_source import CalibrationSource

from app.services import (
    weight_reference_service,
)


# =========================================================
# PARAMETRES V1
# =========================================================

MIN_GAIN_CHANGE = 0.01

DEFAULT_CONFIDENCE = 0.80

ALGORITHM_VERSION = "recalibration-v1"


def propose_from_reference_event(
    expected_delta_kg: float,
    measured_delta_kg: float,
) -> CalibrationProposalDTO:
    """
    =====================================================
    Génère une proposition de calibration
    à partir d'un poids étalon.
    =====================================================

    Exemple :

    attendu :
        +1.000 kg

    mesuré :
        +0.950 kg

    gain :
        1.0526

    => future calibration proposée
    =====================================================
    """

    gain = weight_reference_service.compute_gain_from_reference(
        expected_delta_kg=expected_delta_kg,
        measured_delta_kg=measured_delta_kg,
    )

    return CalibrationProposalDTO(
        offset_kg=0.0,
        gain=gain,
        confidence=DEFAULT_CONFIDENCE,
        source=CalibrationSource.REFERENCE_WEIGHT,
        algorithm_version=ALGORITHM_VERSION,
    )


def propose_from_baseline_drift(
    baseline_weight: float,
    current_weight: float,
) -> CalibrationProposalDTO:
    """
    =====================================================
    Détection simple d'offset.

    Exemple :

    baseline :
        50.0 kg

    poids observé :
        51.2 kg

    dérive :
        +1.2 kg

    => offset = +1.2
    =====================================================
    """

    offset = current_weight - baseline_weight

    return CalibrationProposalDTO(
        offset_kg=offset,
        gain=1.0,
        confidence=DEFAULT_CONFIDENCE,
        source=CalibrationSource.AUTO_DRIFT,
        algorithm_version=ALGORITHM_VERSION,
    )
