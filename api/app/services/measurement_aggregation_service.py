from datetime import UTC
from datetime import datetime
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.measurement_5m import Measurement5m
from app.models.measurement_raw import MeasurementRaw
from app.models.sensor_device import SensorDevice


BUCKET_MINUTES = 5


def floor_to_5_minutes(
    dt: datetime,
) -> datetime:
    """
    =========================================================
    Arrondit une date au bucket inférieur.

    Exemple :

    14:07 -> 14:05
    14:13 -> 14:10
    =========================================================
    """

    minute = (dt.minute // BUCKET_MINUTES) * BUCKET_MINUTES

    return dt.replace(
        minute=minute,
        second=0,
        microsecond=0,
    )


def aggregate_measurements_5m(
    db: Session,
) -> None:
    """
    =========================================================
    Agrège tous les buckets 5 minutes terminés
    non encore traités.
    =========================================================

    IMPORTANT :
    On n'agrège JAMAIS le bucket courant.

    Pourquoi ?

    Car les données peuvent encore arriver :
    - buffer Raspberry
    - latence réseau
    - upload batch

    Exemple :
    à 14:23

    on agrège :
    - 14:00
    - 14:05
    - 14:10
    - 14:15

    mais PAS :
    - 14:20
    =========================================================
    """

    now = datetime.now(UTC)

    current_bucket = floor_to_5_minutes(now)

    # =====================================================
    # Dernier bucket déjà agrégé
    # =====================================================
    last_bucket = db.query(
        func.max(Measurement5m.bucket_at),
    ).scalar()

    # =====================================================
    # Premier lancement :
    # on commence au plus ancien RAW.
    # =====================================================
    if last_bucket is None:
        oldest_raw = db.query(
            func.min(MeasurementRaw.measured_at),
        ).scalar()

        if oldest_raw is None:
            print("No RAW data found.")
            return

        bucket = floor_to_5_minutes(oldest_raw)

    else:
        bucket = last_bucket + timedelta(
            minutes=BUCKET_MINUTES,
        )

    # =====================================================
    # Boucle bucket par bucket
    # =====================================================
    while bucket < current_bucket:
        bucket_end = bucket + timedelta(
            minutes=BUCKET_MINUTES,
        )

        print(f"Aggregating bucket: {bucket}")

        # =================================================
        # GROUP BY métier
        #
        # IMPORTANT :
        # séparation par :
        # - type
        # - ruche
        # - sensor
        # - hive_level
        # =================================================
        results = (
            db.query(
                MeasurementRaw.type,
                SensorDevice.hive_id,
                MeasurementRaw.sensor_device_id,
                MeasurementRaw.hive_level_id,
                func.avg(MeasurementRaw.value),
                func.min(MeasurementRaw.value),
                func.max(MeasurementRaw.value),
                func.count(MeasurementRaw.id),
            )
            .join(
                SensorDevice,
                SensorDevice.id == MeasurementRaw.sensor_device_id,
            )
            .filter(
                MeasurementRaw.measured_at >= bucket,
            )
            .filter(
                MeasurementRaw.measured_at < bucket_end,
            )
            .group_by(
                MeasurementRaw.type,
                SensorDevice.hive_id,
                MeasurementRaw.sensor_device_id,
                MeasurementRaw.hive_level_id,
            )
            .all()
        )

        for result in results:
            agg = Measurement5m(
                bucket_at=bucket,
                type=result[0],
                hive_id=result[1],
                sensor_device_id=result[2],
                hive_level_id=result[3],
                avg_value=result[4],
                min_value=result[5],
                max_value=result[6],
                samples_count=result[7],
            )

            db.add(agg)

        db.commit()

        bucket = bucket_end

    print("Aggregation completed.")
