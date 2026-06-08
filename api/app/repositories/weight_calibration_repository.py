from datetime import datetime

from sqlalchemy.orm import Session

from app.models.weight_calibration import WeightCalibration


def create(
    db: Session,
    calibration: WeightCalibration,
) -> WeightCalibration:
    """
    =========================================================
    Persiste une calibration.
    =========================================================
    """

    db.add(calibration)

    db.commit()

    db.refresh(calibration)

    return calibration


def update(
    db: Session,
    calibration: WeightCalibration,
) -> WeightCalibration:
    """
    =========================================================
    Persiste les modifications d'une calibration.
    =========================================================
    """

    db.commit()

    db.refresh(calibration)

    return calibration


def get_by_id(
    db: Session,
    calibration_id: int,
) -> WeightCalibration | None:
    """
    =========================================================
    Recherche par identifiant.
    =========================================================
    """

    return (
        db.query(WeightCalibration)
        .filter(
            WeightCalibration.id == calibration_id,
        )
        .first()
    )


def get_all(
    db: Session,
) -> list[WeightCalibration]:
    """
    =========================================================
    Retourne toutes les calibrations.
    =========================================================
    """

    return (
        db.query(WeightCalibration)
        .order_by(
            WeightCalibration.valid_from.desc(),
        )
        .all()
    )


def get_current_for_hive_level(
    db: Session,
    hive_level_id: int,
) -> WeightCalibration | None:
    """
    =========================================================
    Calibration actuellement active.

    Convention métier :

    valid_to = NULL
        => calibration active
    =========================================================
    """

    return (
        db.query(WeightCalibration)
        .filter(
            WeightCalibration.hive_level_id
            == hive_level_id,
        )
        .filter(
            WeightCalibration.valid_to.is_(None),
        )
        .first()
    )


def close_current_calibration(
    db: Session,
    hive_level_id: int,
    closed_at: datetime,
) -> None:
    """
    =========================================================
    Ferme la calibration actuellement active.

    IMPORTANT :

    Une seule calibration peut être active
    simultanément pour une balance.
    =========================================================
    """

    calibration = get_current_for_hive_level(
        db=db,
        hive_level_id=hive_level_id,
    )

    if calibration is None:
        return

    calibration.valid_to = closed_at

    db.commit()