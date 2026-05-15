from sqlalchemy.orm import Session

from fastapi import APIRouter
from fastapi import Depends

from app.database import get_db

from datetime import datetime

from app.schemas.weighing import WeighingCreate
from app.schemas.weighing import WeighingRead

from app.services import weighing_service


router = APIRouter(
    prefix="/weighings",
    tags=["Weighings"],
)


@router.post(
    "",
    response_model=WeighingRead,
)
def create_weighing(
    weighing: WeighingCreate,
    db: Session = Depends(get_db),
):
    return weighing_service.create_weighing(
        db=db,
        weighing=weighing,
    )


@router.get(
    "/{weighing_id}",
    response_model=WeighingRead,
)
def get_weighing(
    weighing_id: int,
    db: Session = Depends(get_db),
):
    return weighing_service.get_weighing_by_id(
        db=db,
        weighing_id=weighing_id,
    )


@router.get(
    "",
    response_model=list[WeighingRead],
)
def get_weighings(
    level_id: int | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return weighing_service.get_weighings(
        db=db,
        level_id=level_id,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )