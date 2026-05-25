from datetime import datetime

from sqlalchemy.orm import Session

from app.models.measurement_5m import Measurement5m


def get_all(
    db: Session,
    measurement_type: str | None = None,
    hive_level_id: int | None = None,
    sensor_device_id: int | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> list[Measurement5m]:
    """
    =========================================================
    Lecture des données agrégées.

    IMPORTANT :
    - utilisé par Plotly
    - utilisé par le dashboard
    - ne touche jamais les données RAW
    =========================================================
    """

    query = db.query(Measurement5m)

    # =========================================================
    # Filtre par type :
    # temperature / humidity / co2 / weight
    # =========================================================
    if measurement_type is not None:
        query = query.filter(
            Measurement5m.type == measurement_type,
        )

    if hive_level_id is not None:
        query = query.filter(
            Measurement5m.hive_level_id == hive_level_id,
        )

    if sensor_device_id is not None:
        query = query.filter(
            Measurement5m.sensor_device_id == sensor_device_id,
        )

    if start_at is not None:
        query = query.filter(
            Measurement5m.bucket_at >= start_at,
        )

    if end_at is not None:
        query = query.filter(
            Measurement5m.bucket_at <= end_at,
        )

    query = query.order_by(
        Measurement5m.bucket_at.asc(),
    )

    return query.all()