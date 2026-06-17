from unittest.mock import Mock
from unittest.mock import patch

from app.models.weight_baseline import (
    WeightBaseline,
)

from app.services import (
    baseline_detection_service,
)

# Fenêtre insuffisante
@patch(
    "app.services.baseline_detection_service."
    "measurement_corrected_repository"
)
def test_detect_latest_baseline_not_enough_data(
    mock_repository,
):

    mock_repository.get_latest_for_hive_level.return_value = []

    result = (
        baseline_detection_service
        .detect_latest_baseline(
            db=Mock(),
            hive_level_id=1,
        )
    )

    assert result is None


# Fenêtre non stable
@patch(
    "app.services.baseline_detection_service."
    "measurement_corrected_repository"
)
@patch(
    "app.services.baseline_detection_service."
    "weight_baseline_service"
)
def test_detect_latest_baseline_unstable(
    mock_baseline_service,
    mock_repository,
):

    mock_repository.get_latest_for_hive_level.return_value = [
        Mock(corrected_weight_kg=50)
        for _ in range(6)
    ]

    mock_baseline_service.detect_baseline_candidate.return_value = None

    result = (
        baseline_detection_service
        .detect_latest_baseline(
            db=Mock(),
            hive_level_id=1,
        )
    )

    assert result is None


# Baseline créée
@patch(
    "app.services.baseline_detection_service."
    "measurement_corrected_repository"
)
@patch(
    "app.services.baseline_detection_service."
    "weight_baseline_service"
)
def test_detect_latest_baseline_success(
    mock_baseline_service,
    mock_repository,
):

    mock_repository.get_latest_for_hive_level.return_value = [
        Mock(corrected_weight_kg=50)
        for _ in range(6)
    ]

    candidate = Mock()

    baseline = Mock(
        spec=WeightBaseline,
    )

    (
        mock_baseline_service
        .detect_baseline_candidate
        .return_value
    ) = candidate

    (
        mock_baseline_service
        .save_baseline
        .return_value
    ) = baseline

    result = (
        baseline_detection_service
        .detect_latest_baseline(
            db=Mock(),
            hive_level_id=1,
        )
    )

    assert result == baseline