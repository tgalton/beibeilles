from datetime import UTC
from datetime import datetime

from sqlalchemy.orm import Session

from app.dto.calibration_proposal_dto import (
    CalibrationProposalDTO,
)

from app.enums.calibration_source import (
    CalibrationSource,
)

from app.models.weight_calibration import (
    WeightCalibration,
)

from app.repositories import (
    weight_calibration_repository,
)


def apply_proposal(
    db: Session,
    hive_level_id: int,
    proposal: CalibrationProposalDTO,
) -> WeightCalibration:
    """
    =====================================================
    Applique une proposition de calibration.

    IMPORTANT :

    Une seule calibration active
    par balance.
    =====================================================
    """

    now = datetime.now(UTC)

    weight_calibration_repository.close_current_calibration(
        db=db,
        hive_level_id=hive_level_id,
        closed_at=now,
    )

    calibration = WeightCalibration(
        hive_level_id=hive_level_id,
        valid_from=now,
        offset_kg=proposal.offset_kg,
        gain=proposal.gain,
        source=CalibrationSource(
            proposal.source,
        ),
        algorithm_version=proposal.algorithm_version,
    )

    return (
        weight_calibration_repository
        .create(
            db=db,
            calibration=calibration,
        )
    )