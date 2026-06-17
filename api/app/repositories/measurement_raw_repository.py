from sqlalchemy.orm import Session

from app.models.measurement_raw import MeasurementRaw

from datetime import datetime


def create_many(
    db: Session,
    measurements: list[MeasurementRaw],
) -> list[MeasurementRaw]:
    """
    =========================================================
    Bulk insert des mesures brutes.

    IMPORTANT :
    - ingestion ultra fréquente
    - doit être le plus rapide possible
    - aucun calcul ici
    =========================================================
    """

    db.add_all(measurements)

    db.commit()

    return measurements


def get_by_id(
    db: Session,
    measurement_id: int,
) -> MeasurementRaw | None:
    """
    =========================================================
    Lecture d'une mesure RAW par ID.
    =========================================================
    """

    return (
        db.query(MeasurementRaw)
        .filter(
            MeasurementRaw.id == measurement_id,
        )
        .first()
    )


def get_all(
    db: Session,
    measurement_type: str | None = None,
    hive_level_id: int | None = None,
    sensor_device_id: int | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 1000,
) -> list[MeasurementRaw]:
    """
    =========================================================
    Lecture des mesures RAW.
    =========================================================
    """

    query = db.query(MeasurementRaw)

    if measurement_type is not None:
        query = query.filter(
            MeasurementRaw.type == measurement_type,
        )

    if hive_level_id is not None:
        query = query.filter(
            MeasurementRaw.hive_level_id == hive_level_id,
        )

    if sensor_device_id is not None:
        query = query.filter(
            MeasurementRaw.sensor_device_id == sensor_device_id,
        )

    if start_at is not None:
        query = query.filter(
            MeasurementRaw.measured_at >= start_at,
        )

    if end_at is not None:
        query = query.filter(
            MeasurementRaw.measured_at <= end_at,
        )

    query = query.order_by(
        MeasurementRaw.measured_at.desc(),
    )

    query = query.limit(limit)

    return query.all()
