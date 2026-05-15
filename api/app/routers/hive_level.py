from sqlalchemy.orm import Session

from fastapi import APIRouter
from fastapi import Depends

from app.database import get_db

from app.schemas.hive_level import HiveLevelCreate
from app.schemas.hive_level import HiveLevelRead

from app.services import hive_level_service


router = APIRouter(
    prefix="/hive-levels",
    tags=["HiveLevels"],
)


@router.post(
    "",
    response_model=HiveLevelRead,
)
def create_hive_level(
    hive_level: HiveLevelCreate,
    db: Session = Depends(get_db),
):
    return hive_level_service.create_hive_level(
        db=db,
        hive_level=hive_level,
    )


@router.get(
    "/{level_id}",
    response_model=HiveLevelRead,
)
def get_hive_level(
    level_id: int,
    db: Session = Depends(get_db),
):
    return hive_level_service.get_hive_level_by_id(
        db=db,
        level_id=level_id,
    )


@router.get(
    "",
    response_model=list[HiveLevelRead],
)
def get_hive_levels(
    db: Session = Depends(get_db),
):
    return hive_level_service.get_hive_levels(
        db=db,
    )