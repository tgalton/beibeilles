from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.repositories import hive_repository

from app.schemas.hive import HiveCreate
from app.schemas.hive import HiveUpdate


def create_hive(
    db: Session,
    hive: HiveCreate,
):
    return hive_repository.create(
        db=db,
        name=hive.name,
    )


def get_hives(
    db: Session,
):
    return hive_repository.get_all(db=db)


def get_hive_by_id(
    db: Session,
    hive_id: int,
):
    hive = hive_repository.get_by_id(
        db=db,
        hive_id=hive_id,
    )

    if hive is None:
        raise HTTPException(
            status_code=404,
            detail="Hive not found",
        )

    return hive


def delete_hive(
    db: Session,
    hive_id: int,
):
    hive = get_hive_by_id(
        db=db,
        hive_id=hive_id,
    )

    hive_repository.delete(
        db=db,
        hive=hive,
    )

    return {
        "message": "Hive deleted",
    }


def update_hive(
    db: Session,
    hive_id: int,
    hive_update: HiveUpdate,
):
    hive = get_hive_by_id(
        db=db,
        hive_id=hive_id,
    )

    hive.name = hive_update.name

    return hive_repository.update(
        db=db,
        hive=hive,
    )
