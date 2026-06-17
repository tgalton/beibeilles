from unittest.mock import Mock, patch

from app.services import (
    auto_recalibration_orchestrator,
)
from app.database import SessionLocal

from app.repositories import (
    hive_level_repository,
)


@patch(
    "app.services.auto_recalibration_orchestrator."
    "measurement_5m_repository"
)
def test_run_not_enough_measurements(
    mock_repository,
):
    """
    =====================================================
    Aucun calcul si moins de 6 buckets.
    =====================================================
    """

    mock_repository.get_latest_weight_measurements.return_value = []

    auto_recalibration_orchestrator.run(
        db=None,
        hive_level_id=1,
    )



from unittest.mock import patch


@patch(
    "app.services.auto_recalibration_orchestrator."
    "weight_baseline_service"
)
@patch(
    "app.services.auto_recalibration_orchestrator."
    "measurement_5m_repository"
)
def test_run_unstable_window(
    mock_repository,
    mock_baseline_service,
):
    """
    =====================================================
    Aucun enregistrement si la
    fenêtre est instable.
    =====================================================
    """

    measurements = [
        Mock(avg_value=50.0)
        for _ in range(6)
    ]

    mock_repository.get_latest_weight_measurements.return_value = (
        measurements
    )

    mock_baseline_service.detect_baseline_candidate.return_value = None

    auto_recalibration_orchestrator.run(
        db=None,
        hive_level_id=1,
    )

    mock_baseline_service.save_baseline.assert_not_called()



from unittest.mock import Mock
from unittest.mock import patch

from app.dto.baseline_candidate_dto import (
    BaselineCandidateDTO,
)


# @patch(
#     "app.services.auto_recalibration_orchestrator."
#     "weight_baseline_service"
# )
# @patch(
#     "app.services.auto_recalibration_orchestrator."
#     "measurement_5m_repository"
# )

# def test_run_save_baseline(
#     mock_repository,
#     mock_baseline_service,
# ):
#     """
#     =====================================================
#     Une baseline détectée doit être
#     sauvegardée.
#     =====================================================
#     """

#     measurements = [
#         Mock(avg_value=50.0)
#         for _ in range(6)
#     ]

#     mock_repository.get_latest_weight_measurements.return_value = (
#         measurements
#     )

#     candidate = BaselineCandidateDTO(
#         hive_level_id=1,
#         baseline_offset_kg=50.0,
#         confidence=0.95,
#         stable_duration_minutes=30,
#         algorithm_version="v1",
#     )

#     mock_baseline_service.detect_baseline_candidate.return_value = (
#         candidate
#     )

#     auto_recalibration_orchestrator.run(
#         db=None,
#         hive_level_id=1,
#     )

#     mock_baseline_service.save_baseline.assert_called_once()





def main() -> None:
    """
    =====================================================
    Lance une analyse sur tous
    les niveaux de ruche.
    =====================================================
    """

    db = SessionLocal()

    try:

        hive_levels = (
            hive_level_repository
            .get_all(
                db=db,
            )
        )

        for hive_level in hive_levels:

            auto_recalibration_orchestrator.run(
                db=db,
                hive_level_id=hive_level.id,
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()