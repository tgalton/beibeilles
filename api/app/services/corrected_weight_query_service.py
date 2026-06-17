from datetime import datetime

from sqlalchemy.orm import Session

from app.models.measurement_corrected import (
    MeasurementCorrected,
)

from app.repositories import (
    measurement_corrected_repository,
)


def get_latest_weight(
    db: Session,
    hive_level_id: int,
) -> MeasurementCorrected | None:
    """
    =====================================================
    Dernier poids corrigé.

    Utilisé par :

    - dashboard
    - widgets temps réel
    - alertes futures
    =====================================================
    """

    return (
        measurement_corrected_repository
        .get_latest_corrected_weight(
            db=db,
            hive_level_id=hive_level_id,
        )
    )


def get_weight_history(
    db: Session,
    hive_level_id: int,
    start_at: datetime,
    end_at: datetime,
) -> list[MeasurementCorrected]:
    """
    =====================================================
    Historique corrigé.

    Utilisé par :

    - graphiques Plotly
    - exports CSV
    =====================================================
    """

    return (
        measurement_corrected_repository
        .get_corrected_weights_between_dates(
            db=db,
            hive_level_id=hive_level_id,
            start_at=start_at,
            end_at=end_at,
        )
    )