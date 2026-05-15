from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models.weighing import Weighing

from app.repositories import weighing_repository

from app.schemas.weighing import WeighingCreate

from datetime import datetime


def create_weighing(
    db: Session,
    weighing: WeighingCreate,
):
    db_weighing = Weighing(
        weight=weighing.weight,
        level_id=weighing.level_id,
    )

    return weighing_repository.create(
        db=db,
        weighing=db_weighing,
    )


def get_weighings(
    db: Session,
    level_id: int | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
):
    return weighing_repository.get_all(
        db=db,
        level_id=level_id,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )

def get_weighing_by_id(
    db: Session,
    weighing_id: int,
):
    weighing = weighing_repository.get_by_id(
        db=db,
        weighing_id=weighing_id,
    )

    if weighing is None:
        raise HTTPException(
            status_code=404,
            detail="Weighing not found",
        )

    return weighing