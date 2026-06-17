from datetime import UTC
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

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
    recalibration_pipeline_service,
)


@patch("app.services.recalibration_pipeline_service.weight_baseline_service")
def test_pipeline_no_candidate(
    mock_baseline_service,
):

    mock_baseline_service.detect_baseline_candidate.return_value = None

    result = recalibration_pipeline_service.process_stable_window(
        db=Mock(),
        hive_level_id=1,
        reference_baseline=Mock(),
        weights=[50],
        timestamps_minutes=[0],
    )

    assert result is None


@patch("app.services.recalibration_pipeline_service.auto_recalibration_service")
@patch("app.services.recalibration_pipeline_service.weight_baseline_service")
def test_pipeline_no_proposal(
    mock_baseline_service,
    mock_auto_service,
):

    candidate = Mock()

    baseline = WeightBaseline(
        hive_level_id=1,
        baseline_offset_kg=50.0,
        confidence=0.95,
        stable_duration_minutes=60,
        algorithm_version="v1",
        computed_at=datetime.now(UTC),
    )

    mock_baseline_service.detect_baseline_candidate.return_value = candidate

    mock_baseline_service.build_baseline.return_value = baseline

    mock_auto_service.propose_from_baseline_drift.return_value = None

    result = recalibration_pipeline_service.process_stable_window(
        db=Mock(),
        hive_level_id=1,
        reference_baseline=baseline,
        weights=[],
        timestamps_minutes=[],
    )

    assert result is None


@patch("app.services.recalibration_pipeline_service.auto_recalibration_service")
@patch("app.services.recalibration_pipeline_service.weight_baseline_service")
def test_pipeline_create_calibration(
    mock_baseline_service,
    mock_auto_service,
):

    candidate = Mock()

    baseline = WeightBaseline(
        hive_level_id=1,
        baseline_offset_kg=51.2,
        confidence=0.95,
        stable_duration_minutes=60,
        algorithm_version="v1",
        computed_at=datetime.now(UTC),
    )

    calibration = WeightCalibration(
        hive_level_id=1,
        valid_from=datetime.now(UTC),
        valid_to=None,
        offset_kg=1.2,
        gain=1.0,
        source=CalibrationSource.AUTO_DRIFT,
    )

    mock_baseline_service.detect_baseline_candidate.return_value = candidate

    mock_baseline_service.build_baseline.return_value = baseline

    mock_auto_service.propose_from_baseline_drift.return_value = Mock()

    mock_auto_service.create_auto_calibration.return_value = calibration

    result = recalibration_pipeline_service.process_stable_window(
        db=Mock(),
        hive_level_id=1,
        reference_baseline=baseline,
        weights=[],
        timestamps_minutes=[],
    )

    assert result == calibration
