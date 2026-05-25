from datetime import UTC
from datetime import datetime
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.measurement_5m import Measurement5m
from app.models.measurement_raw import MeasurementRaw


BUCKET_MINUTES = 5


def aggregate_last_5_minutes(
    db: Session,
) -> None:
    """
    =========================================================
    Génère les données agrégées 5 minutes.

    IMPORTANT :
    Cette fonction transforme les données RAW
    en données utilisables par Plotly.

    Le but est de réduire massivement
    le nombre de points.

    Exemple :

    300 secondes RAW
    deviennent
    1 ligne agrégée.
    =========================================================
    """

    now = datetime.now(UTC)

    bucket_end = now.replace(
        second=0,
        microsecond=0,
    )

    bucket_start = bucket_end - timedelta(
        minutes=BUCKET_MINUTES,
    )

    results = (
        db.query(
            MeasurementRaw.type,
            MeasurementRaw.sensor_device_id,
            MeasurementRaw.hive_level_id,

            func.avg(MeasurementRaw.value),
            func.min(MeasurementRaw.value),
            func.max(MeasurementRaw.value),
            func.count(MeasurementRaw.id),
        )
        .filter(
            MeasurementRaw.measured_at >= bucket_start,
        )
        .filter(
            MeasurementRaw.measured_at < bucket_end,
        )
        .group_by(
            MeasurementRaw.type,
            MeasurementRaw.sensor_device_id,
            MeasurementRaw.hive_level_id,
        )
        .all()
    )

    for result in results:

        agg = Measurement5m(
            bucket_at=bucket_start,

            type=result[0],

            sensor_device_id=result[1],

            hive_level_id=result[2],

            avg_value=result[3],

            min_value=result[4],

            max_value=result[5],

            samples_count=result[6],
        )

        db.add(agg)

    db.commit()