from datetime import datetime

from sqlalchemy.orm import Session

from app.models.measurement_5m import Measurement5m
from app.models.measurement_corrected import (
    MeasurementCorrected,
)


def create(
    db: Session,
    measurement: MeasurementCorrected,
) -> MeasurementCorrected:
    """
    =====================================================
    Persiste une mesure corrigée.
    =====================================================
    """

    db.add(measurement)

    db.commit()

    db.refresh(measurement)

    return measurement


def update(
    db: Session,
    measurement: MeasurementCorrected,
) -> MeasurementCorrected:
    """
    =====================================================
    Persiste les modifications.
    =====================================================
    """

    db.commit()

    db.refresh(measurement)

    return measurement


def get_by_measurement_5m_id(
    db: Session,
    measurement_5m_id: int,
) -> MeasurementCorrected | None:
    """
    =====================================================
    Recherche par bucket source.

    Une seule mesure corrigée est
    autorisée par Measurement5m.
    =====================================================
    """

    return (
        db.query(MeasurementCorrected)
        .filter(MeasurementCorrected.measurement_5m_id == measurement_5m_id)
        .first()
    )


def delete_from_date(
    db: Session,
    hive_level_id: int,
    measured_at: datetime,
) -> None:
    """
    =====================================================
    Supprime toutes les corrections à partir
    d'une date donnée.

    Utilisé lors d'un recalcul historique.
    =====================================================
    """

    (
        db.query(
            MeasurementCorrected,
        )
        .join(
            Measurement5m,
            Measurement5m.id == MeasurementCorrected.measurement_5m_id,
        )
        .filter(
            Measurement5m.hive_level_id == hive_level_id,
        )
        .filter(
            Measurement5m.bucket_at >= measured_at,
        )
        .delete()
    )

    db.commit()


def get_after_date(
    db: Session,
    hive_level_id: int,
    measured_at: datetime,
) -> list[MeasurementCorrected]:
    """
    Retourne toutes les mesures corrigées
    après une date donnée.
    """

    return (
        db.query(
            MeasurementCorrected,
        )
        .join(
            Measurement5m,
            Measurement5m.id == MeasurementCorrected.measurement_5m_id,
        )
        .filter(
            Measurement5m.hive_level_id == hive_level_id,
        )
        .filter(
            Measurement5m.bucket_at >= measured_at,
        )
        .order_by(
            Measurement5m.bucket_at.asc(),
        )
        .all()
    )


def get_latest_for_hive_level(
    db: Session,
    hive_level_id: int,
    limit: int,
) -> list[MeasurementCorrected]:
    """
    =====================================================
    Retourne les derniers buckets corrigés
    d'un niveau de ruche.
    =====================================================
    """

    return (
        db.query(
            MeasurementCorrected,
        )
        .join(
            Measurement5m,
            Measurement5m.id == MeasurementCorrected.measurement_5m_id,
        )
        .filter(
            Measurement5m.hive_level_id == hive_level_id,
        )
        .order_by(
            Measurement5m.bucket_at.desc(),
        )
        .limit(limit)
        .all()
    )


def upsert(
    db: Session,
    measurement: MeasurementCorrected,
) -> MeasurementCorrected:
    """
    =====================================================
    Insert ou remplace une mesure corrigée.

    Utilisé lors des recalculs historiques.
    =====================================================
    """

    existing = get_by_measurement_5m_id(
        db=db,
        measurement_5m_id=(measurement.measurement_5m_id),
    )

    if existing is None:
        return create(
            db=db,
            measurement=measurement,
        )

    existing.calibration_id = measurement.calibration_id

    existing.raw_weight_kg = measurement.raw_weight_kg

    existing.corrected_weight_kg = measurement.corrected_weight_kg

    db.commit()

    db.refresh(
        existing,
    )

    return existing


def get_latest_corrected_weight(
    db: Session,
    hive_level_id: int,
) -> MeasurementCorrected | None:
    """
    =====================================================
    Dernier poids corrigé disponible.

    Utilisé par :

    - dashboard
    - widgets temps réel
    - alertes futures
    =====================================================
    """

    return (
        db.query(
            MeasurementCorrected,
        )
        .join(
            Measurement5m,
            Measurement5m.id == MeasurementCorrected.measurement_5m_id,
        )
        .filter(
            Measurement5m.hive_level_id == hive_level_id,
        )
        .order_by(
            Measurement5m.bucket_at.desc(),
        )
        .first()
    )


def get_corrected_weights_between_dates(
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
    - analyses futures
    =====================================================
    """

    return (
        db.query(
            MeasurementCorrected,
        )
        .join(
            Measurement5m,
            Measurement5m.id == MeasurementCorrected.measurement_5m_id,
        )
        .filter(
            Measurement5m.hive_level_id == hive_level_id,
        )
        .filter(
            Measurement5m.bucket_at >= start_at,
        )
        .filter(
            Measurement5m.bucket_at <= end_at,
        )
        .order_by(
            Measurement5m.bucket_at.asc(),
        )
        .all()
    )
