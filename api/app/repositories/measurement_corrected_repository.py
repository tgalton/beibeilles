from datetime import datetime

from sqlalchemy.orm import Session

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


def get_by_measurement_5m(
    db: Session,
    measurement_5m_id: int,
) -> MeasurementCorrected | None:
    """
    =====================================================
    Retourne la mesure corrigée
    associée à un bucket.
    =====================================================
    """

    return (
        db.query(
            MeasurementCorrected,
        )
        .filter(
            MeasurementCorrected.measurement_5m_id
            == measurement_5m_id,
        )
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
        .filter(
            MeasurementCorrected.hive_level_id
            == hive_level_id,
        )
        .filter(
            MeasurementCorrected.measured_at
            >= measured_at,
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
        .filter(
            MeasurementCorrected.hive_level_id
            == hive_level_id,
        )
        .filter(
            MeasurementCorrected.measured_at
            >= measured_at,
        )
        .order_by(
            MeasurementCorrected.measured_at.asc(),
        )
        .all()
    )