from unittest.mock import Mock
from unittest.mock import patch
from app.enums.calibration_source import CalibrationSource
from app.dto.calibration_proposal_dto import (
    CalibrationProposalDTO,
)

from app.services import (
    calibration_application_service,
)


@patch("app.services.calibration_application_service.weight_calibration_repository")
def test_apply_proposal(
    mock_repository,
):
    """
    =====================================================
    Vérifie :

    - fermeture calibration active
    - création nouvelle calibration
    =====================================================
    """

    proposal = CalibrationProposalDTO(
        offset_kg=1.2,
        gain=1.0,
        confidence=0.8,
        source=CalibrationSource.AUTO_DRIFT,
        algorithm_version="v1",
    )

    db = Mock()

    calibration_application_service.apply_proposal(
        db=db,
        hive_level_id=1,
        proposal=proposal,
    )

    mock_repository.close_current_calibration.assert_called_once()

    mock_repository.create.assert_called_once()
