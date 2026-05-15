from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models.hive_level import HiveLevel

from app.repositories import hive_level_repository

from app.schemas.hive_level import HiveLevelCreate


def create_hive_level(
    db: Session,
    hive_level: HiveLevelCreate,
):
    db_hive_level = HiveLevel(
        name=hive_level.name,
        hive_id=hive_level.hive_id,
        lower_level_id=hive_level.lower_level_id,
        upper_level_id=hive_level.upper_level_id,
    )

    return hive_level_repository.create(
        db=db,
        hive_level=db_hive_level,
    )


def get_hive_levels(
    db: Session,
):
    return hive_level_repository.get_all(db=db)


def get_hive_level_by_id(
    db: Session,
    level_id: int,
):
    level = hive_level_repository.get_by_id(
        db=db,
        level_id=level_id,
    )

    if level is None:
        raise HTTPException(
            status_code=404,
            detail="Hive level not found",
        )

    return level