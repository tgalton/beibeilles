from datetime import UTC
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

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
    auto_recalibration_service,
)


def test_propose_from_baseline_drift_too_small():

    reference = WeightBaseline(
        hive_level_id=1,
        baseline_offset_kg=50.0,
        confidence=0.95,
        stable_duration_minutes=60,
        algorithm_version="v1",
        computed_at=datetime.now(UTC),
    )

    current = WeightBaseline(
        hive_level_id=1,
        baseline_offset_kg=50.1,
        confidence=0.95,
        stable_duration_minutes=60,
        algorithm_version="v1",
        computed_at=datetime.now(UTC),
    )

    proposal = auto_recalibration_service.propose_from_baseline_drift(
        reference,
        current,
    )

    assert proposal is None


def test_propose_from_baseline_drift_negative():

    reference = WeightBaseline(
        hive_level_id=1,
        baseline_offset_kg=50.0,
        confidence=0.95,
        stable_duration_minutes=60,
        algorithm_version="v1",
        computed_at=datetime.now(UTC),
    )

    current = WeightBaseline(
        hive_level_id=1,
        baseline_offset_kg=48.7,
        confidence=0.95,
        stable_duration_minutes=60,
        algorithm_version="v1",
        computed_at=datetime.now(UTC),
    )

    proposal = auto_recalibration_service.propose_from_baseline_drift(
        reference,
        current,
    )

    assert proposal is not None

    assert proposal.offset_kg == -1.3


@patch(
    "app.services.auto_recalibration_service.weight_calibration_repository"
)
@patch(
    "app.services.auto_recalibration_service.weight_calibration_service"
)
def test_create_auto_calibration(
    mock_service,
    mock_repository,
):

    proposal = CalibrationProposalDTO(
        offset_kg=1.2,
        gain=1.0,
        confidence=0.95,
        source=CalibrationSource.AUTO_DRIFT,
        algorithm_version="v1",
    )

    mock_service.get_current_calibration.return_value = None

    calibration = WeightCalibration(
        hive_level_id=1,
        valid_from=datetime.now(UTC),
        valid_to=None,
        offset_kg=1.2,
        gain=1.0,
        source=CalibrationSource.AUTO_DRIFT,
    )

    mock_repository.create.return_value = calibration

    db = Mock()

    result = auto_recalibration_service.create_auto_calibration(
        db=db,
        hive_level_id=1,
        proposal=proposal,
    )

    assert result == calibration

