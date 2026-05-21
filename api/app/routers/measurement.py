from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.measurement import (
    MeasurementRead,
)

from app.services import measurement_service
from app.schemas.iot_ingest import IoTIngest



router = APIRouter(
    prefix="/measurements",
    tags=["Measurements"],
)


@router.get(
    "/{measurement_id}",
    response_model=MeasurementRead,
)
def get_measurement(
    measurement_id: int,
    db: Session = Depends(get_db),
):

    return measurement_service.get_measurement_by_id(
        db=db,
        measurement_id=measurement_id,
    )


@router.get(
    "",
    response_model=list[MeasurementRead],
)
def get_measurements(
    measurement_type: str | None = None,
    hive_level_id: int | None = None,
    sensor_device_id: int | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):

    return measurement_service.get_measurements(
        db=db,
        measurement_type=measurement_type,
        hive_level_id=hive_level_id,
        sensor_device_id=sensor_device_id,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )
    

@router.post(
    "/ingest",
    response_model=list[MeasurementRead],
)
def ingest_measurements(
    payload: IoTIngest,
    db: Session = Depends(get_db),
):

    return measurement_service.ingest_measurements(
        db=db,
        payload=payload,
    )