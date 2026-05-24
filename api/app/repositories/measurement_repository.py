from datetime import datetime

from sqlalchemy.orm import Session

from app.models.measurement import Measurement


def create(
    db: Session,
    measurement: Measurement,
) -> Measurement:

    db.add(measurement)

    db.commit()

    db.refresh(measurement)

    return measurement


def create_many(
    db: Session,
    measurements: list[Measurement],
) -> list[Measurement]:

    # =========================================================
    # bulk save des mesures IoT
    # plus efficace que commit unitaire
    # =========================================================
    db.add_all(measurements)

    db.commit()

    for measurement in measurements:
        db.refresh(measurement)

    return measurements


def get_by_id(
    db: Session,
    measurement_id: int,
) -> Measurement | None:

    return (
        db.query(Measurement)
        .filter(
            Measurement.id == measurement_id,
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
    limit: int | None= 10000,
) -> list[Measurement]:

    query = db.query(Measurement)

    # =========================================================
    # Filtre par type :
    # temperature / humidity / co2 / weight
    # =========================================================
    if measurement_type is not None:
        query = query.filter(
            Measurement.type == measurement_type,
        )

    if hive_level_id is not None:
        query = query.filter(
            Measurement.hive_level_id == hive_level_id,
        )

    if sensor_device_id is not None:
        query = query.filter(
            Measurement.sensor_device_id
            == sensor_device_id,
        )

    if start_at is not None:
        query = query.filter(
            Measurement.measured_at >= start_at,
        )

    if end_at is not None:
        query = query.filter(
            Measurement.measured_at <= end_at,
        )
        

    query = query.order_by(
        Measurement.measured_at.desc(),
    )

    if limit is not None:
        query = query.limit(limit)

    return query.all()