
from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Query, Session

from app.database import get_db

from app.services import measurement_5m_service

from dateutil.parser import isoparse


router = APIRouter(
    prefix="/measurements/5m",
    tags=["Measurements 5m"],
)


@router.get("")
def get_measurements_5m(
    measurement_type: str | None = None,
    hive_level_id: int | None = None,
    sensor_device_id: int | None = None,
    start_at: str | None = Query(default=None),
    end_at: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    =========================================================
    Endpoint principal du dashboard.

    IMPORTANT :
    Plotly doit utiliser UNIQUEMENT cet endpoint.

    Ce endpoint retourne des données déjà agrégées.
    =========================================================
    """
    start_dt = isoparse(start_at) if start_at else None
    end_dt = isoparse(end_at) if end_at else None

    return measurement_5m_service.get_measurements_5m(
        db=db,
        measurement_type=measurement_type,
        hive_level_id=hive_level_id,
        sensor_device_id=sensor_device_id,
        start_at=start_dt,
        end_at=end_dt,
    )