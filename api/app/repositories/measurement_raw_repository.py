from sqlalchemy.orm import Session

from app.models.measurement_raw import MeasurementRaw


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

    return (
        db.query(MeasurementRaw)
        .filter(
            MeasurementRaw.id == measurement_id,
        )
        .first()
    )
