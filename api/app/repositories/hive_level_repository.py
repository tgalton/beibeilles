from sqlalchemy.orm import Session

from app.models.hive_level import HiveLevel


def create(
    db: Session,
    hive_level: HiveLevel,
) -> HiveLevel:
    db.add(hive_level)

    db.commit()

    db.refresh(hive_level)

    return hive_level


def get_all(
    db: Session,
) -> list[HiveLevel]:
    """
    =====================================================
    Retourne tous les niveaux de ruche.
    =====================================================
    """

    return db.query(
        HiveLevel,
    ).all()


def get_by_id(
    db: Session,
    level_id: int,
) -> HiveLevel | None:
    return db.query(HiveLevel).filter(HiveLevel.id == level_id).first()
