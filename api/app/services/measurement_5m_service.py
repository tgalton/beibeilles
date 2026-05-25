from datetime import datetime

from sqlalchemy.orm import Session

from app.models.measurement_5m import Measurement5m

from app.repositories import measurement_5m_repository


def get_measurements_5m(
    db: Session,
    measurement_type: str | None = None,
    hive_level_id: int | None = None,
    sensor_device_id: int | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> list[Measurement5m]:
    """
    =========================================================
    Lecture des données agrégées 5 minutes.
    =========================================================

    IMPORTANT :
    utilisé exclusivement par :
    - Plotly
    - dashboards
    - analytics

    Ces données sont déjà agrégées.
    =========================================================
    """

    return measurement_5m_repository.get_all(
        db=db,
        measurement_type=measurement_type,
        hive_level_id=hive_level_id,
        sensor_device_id=sensor_device_id,
        start_at=start_at,
        end_at=end_at,
    )