from sqlalchemy.orm import Session

from fastapi import APIRouter
from fastapi import Depends

from app.database import get_db

from app.schemas.hive import HiveCreate
from app.schemas.hive import HiveRead
from app.schemas.hive import HiveUpdate

from app.services import hive_service


router = APIRouter(
    prefix="/hives",
    tags=["Hives"],
)


@router.post(
    "",
    response_model=HiveRead,
)
def create_hive(
    hive: HiveCreate,
    db: Session = Depends(get_db),
):
    return hive_service.create_hive(
        db=db,
        hive=hive,
    )


@router.get(
    "",
    response_model=list[HiveRead],
)
def get_hives(
    db: Session = Depends(get_db),
):
    return hive_service.get_hives(db=db)


@router.get(
    "/{hive_id}",
    response_model=HiveRead,
)
def get_hive(
    hive_id: int,
    db: Session = Depends(get_db),
):
    return hive_service.get_hive_by_id(
        db=db,
        hive_id=hive_id,
    )


@router.delete("/{hive_id}")
def delete_hive(
    hive_id: int,
    db: Session = Depends(get_db),
):
    return hive_service.delete_hive(
        db=db,
        hive_id=hive_id,
    )


@router.put(
    "/{hive_id}",
    response_model=HiveRead,
)
def update_hive(
    hive_id: int,
    hive_update: HiveUpdate,
    db: Session = Depends(get_db),
):
    return hive_service.update_hive(
        db=db,
        hive_id=hive_id,
        hive_update=hive_update,
    )
