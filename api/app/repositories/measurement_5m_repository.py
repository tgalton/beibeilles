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



def get_weight_measurements_for_hive_level(
    db: Session,
    hive_level_id: int,
) -> list[Measurement5m]:
    """
    =====================================================
    Retourne tous les buckets poids
    d'un niveau de ruche.
    =====================================================
    """

    return (
        db.query(
            Measurement5m,
        )
        .filter(
            Measurement5m.hive_level_id
            == hive_level_id,
        )
        .filter(
            Measurement5m.type == "weight",
        )
        .order_by(
            Measurement5m.bucket_at.asc(),
        )
        .all()
    )

def get_latest_weight_measurements(
    db: Session,
    hive_level_id: int,
    limit: int,
) -> list[Measurement5m]:
    """
    =====================================================
    Retourne les N derniers buckets poids.

    IMPORTANT :

    On récupère d'abord les plus récents,
    puis on réinverse l'ordre afin de
    retrouver une chronologie naturelle.

    Exemple :

    limit = 6

    => 30 dernières minutes
    =====================================================
    """

    measurements = (
        db.query(
            Measurement5m,
        )
        .filter(
            Measurement5m.hive_level_id
            == hive_level_id,
        )
        .filter(
            Measurement5m.type == "weight",
        )
        .order_by(
            Measurement5m.bucket_at.desc(),
        )
        .limit(
            limit,
        )
        .all()
    )

    return list(
        reversed(
            measurements,
        )
    )


def get_between_dates(
    db: Session,
    hive_level_id: int,
    start_at: datetime,
    end_at: datetime,
) -> list[Measurement5m]:
    """
    =====================================================
    Retourne les buckets compris dans
    une période donnée.
    =====================================================
    """

    return (
        db.query(
            Measurement5m,
        )
        .filter(
            Measurement5m.hive_level_id
            == hive_level_id,
        )
        .filter(
            Measurement5m.type == "weight",
        )
        .filter(
            Measurement5m.bucket_at
            >= start_at,
        )
        .filter(
            Measurement5m.bucket_at
            <= end_at,
        )
        .order_by(
            Measurement5m.bucket_at.asc(),
        )
        .all()
    )