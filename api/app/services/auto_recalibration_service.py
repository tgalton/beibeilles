from datetime import UTC
from datetime import datetime

from sqlalchemy.orm import Session

from app.dto.calibration_proposal_dto import (
    CalibrationProposalDTO,
)
from app.enums.calibration_source import (
    CalibrationSource,
)
from app.models.weight_baseline import (
    WeightBaseline,
)
from app.models.weight_calibration import (
    WeightCalibration,
)
from app.services import (
    weight_calibration_service,
)
from app.repositories import (
    weight_calibration_repository,
)

# =========================================================
# PARAMETRES METIER
# =========================================================
#
# En dessous de ce seuil :
#
# -> bruit
# -> imprécision normale
# -> tassement mécanique mineur
#
# donc aucune recalibration.
# =========================================================

MIN_DRIFT_KG = 0.25

MIN_CONFIDENCE = 0.80


def propose_from_baseline_drift(
    reference_baseline: WeightBaseline,
    current_baseline: WeightBaseline,
) -> CalibrationProposalDTO | None:
    """
    =====================================================
    Compare deux baselines.
    =====================================================

    Exemple :

    baseline historique :
        50.0 kg

    baseline récente :
        51.2 kg

    dérive :
        +1.2 kg

    => proposition AUTO_DRIFT
    =====================================================
    """

    drift_kg = (
        current_baseline.baseline_offset_kg - reference_baseline.baseline_offset_kg
    )

    confidence = min(
        reference_baseline.confidence,
        current_baseline.confidence,
    )

    if not should_recalibrate(
        drift_kg=drift_kg,
        confidence=confidence,
    ):
        return None

    return CalibrationProposalDTO(
        offset_kg=round(
            drift_kg,
            3,
        ),
        gain=1.0,
        confidence=confidence,
        source=CalibrationSource.AUTO_DRIFT,
        algorithm_version="v1",
    )


def should_recalibrate(
    drift_kg: float,
    confidence: float,
) -> bool:
    """
    =====================================================
    Décision métier.
    =====================================================

    Conditions :

    - dérive suffisante
    - confiance suffisante
    =====================================================
    """

    return abs(drift_kg) >= MIN_DRIFT_KG and confidence >= MIN_CONFIDENCE


def create_auto_calibration(
    db: Session,
    hive_level_id: int,
    proposal: CalibrationProposalDTO,
) -> WeightCalibration:
    """
    =====================================================
    Applique une proposition AUTO_DRIFT.
    =====================================================

    IMPORTANT :

    Une seule calibration active
    à la fois.

    L'ancienne est fermée avant
    création de la nouvelle.
    =====================================================
    """

    now = datetime.now(UTC)

    current_calibration = weight_calibration_service.get_current_calibration(
        db=db,
        hive_level_id=hive_level_id,
    )

    if current_calibration is not None:
        current_calibration.valid_to = now

        weight_calibration_repository.update(
            db=db,
            calibration=current_calibration,
        )

    calibration = WeightCalibration(
        hive_level_id=hive_level_id,
        valid_from=now,
        valid_to=None,
        offset_kg=proposal.offset_kg,
        gain=proposal.gain,
        source=proposal.source,
        algorithm_version="auto_recalibration_v1",
    )

    return weight_calibration_repository.create(
        db=db,
        calibration=calibration,
    )
