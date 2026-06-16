from datetime import UTC
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

from app.models.measurement_5m import (
    Measurement5m,
)
from app.models.weight_calibration import (
    WeightCalibration,
)
from app.enums.calibration_source import (
    CalibrationSource,
)

from app.services import (
    measurement_corrected_service,
)

@patch(
    "app.services.measurement_corrected_service."
    "measurement_corrected_repository"
)
@patch(
    "app.services.measurement_corrected_service."
    "weight_calibration_service"
)
def test_create_corrected_measurement(
    mock_calibration_service,
    mock_repository,
):
    """
    =====================================================
    Vérifie la création complète
    d'une mesure corrigée.
    =====================================================
    """

    measurement = Measurement5m(
        id=1,
        bucket_at=datetime.now(UTC),
        type="weight",
        hive_id=1,
        sensor_device_id=1,
        hive_level_id=1,
        avg_value=50.0,
        min_value=49.8,
        max_value=50.2,
        samples_count=10,
    )

    calibration = WeightCalibration(
        id=42,
        hive_level_id=1,
        valid_from=datetime.now(UTC),
        valid_to=None,
        offset_kg=-1.0,
        gain=1.0,
        source=CalibrationSource.AUTO_DRIFT,
    )

    mock_calibration_service.get_calibration_for_datetime.return_value = (
        calibration
    )

    mock_calibration_service.apply_calibration.return_value = (
        51.0
    )

    db = Mock()

    (
        measurement_corrected_service
        .create_from_measurement_5m(
            db=db,
            measurement=measurement,
        )
    )

    mock_repository.create.assert_called_once()



@patch(
    "app.services.measurement_corrected_service."
    "measurement_corrected_repository"
)
@patch(
    "app.services.measurement_corrected_service."
    "weight_calibration_service"
)
def test_create_corrected_measurement_without_calibration(
    mock_calibration_service,
    mock_repository,
):
    """
    =====================================================
    Si aucune calibration n'existe,
    calibration_id doit rester NULL.
    =====================================================
    """

    measurement = Measurement5m(
        id=1,
        bucket_at=datetime.now(UTC),
        type="weight",
        hive_id=1,
        sensor_device_id=1,
        hive_level_id=1,
        avg_value=50.0,
        min_value=49.8,
        max_value=50.2,
        samples_count=10,
    )

    mock_calibration_service.get_calibration_for_datetime.return_value = (
        None
    )

    mock_calibration_service.apply_calibration.return_value = (
        50.0
    )

    db = Mock()

    (
        measurement_corrected_service
        .create_from_measurement_5m(
            db=db,
            measurement=measurement,
        )
    )

    created_measurement = (
        mock_repository.create
        .call_args.kwargs["measurement"]
    )

    assert (
        created_measurement.calibration_id
        is None
    )