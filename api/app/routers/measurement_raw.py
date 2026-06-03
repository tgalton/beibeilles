from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.iot_ingest import IoTIngest

from app.schemas.measurement import (
    MeasurementRead,
)

from app.services import measurement_raw_service


router = APIRouter(
    prefix="/measurements",
    tags=["Measurements RAW"],
)

@router.post(
    "/raw/ingest",
    response_model=list[MeasurementRead],)
@router.post(
    "/ingest",
    response_model=list[MeasurementRead],
)
def ingest_measurements(
    payload: IoTIngest,
    db: Session = Depends(get_db),
):
    """
    =========================================================
    Endpoint principal d'ingestion IoT.
    =========================================================

    Les Raspberry envoient leurs données ici.

    IMPORTANT :
    - données BRUTES uniquement
    - aucune agrégation ici
    - aucune logique métier ici

    Objectif :
    garder une ingestion la plus rapide possible.
    =========================================================
    """

    return measurement_raw_service.ingest_measurements(
        db=db,
        payload=payload,
    )


@router.get(
    "/id/{measurement_id}",
    response_model=MeasurementRead,
)
def get_measurement_raw(
    measurement_id: int,
    db: Session = Depends(get_db),
):
    """
    =========================================================
    Lecture d'une mesure RAW unique.
    =========================================================

    Principalement utile pour :
    - debug
    - inspection capteur
    - tests techniques
    =========================================================
    """

    return measurement_raw_service.get_measurement_by_id(
        db=db,
        measurement_id=measurement_id,
    )


@router.get(
    "",
    response_model=list[MeasurementRead],
)
def get_measurements_raw(
    measurement_type: str | None = None,
    hive_level_id: int | None = None,
    sensor_device_id: int | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 1000,
    db: Session = Depends(get_db),
):
    """
    =========================================================
    Lecture des données RAW.
    =========================================================

    IMPORTANT :
    - endpoint technique
    - ne pas utiliser pour Plotly long terme
    - réservé debug / inspection

    Les dashboards doivent utiliser :
    /measurements/5m
    =========================================================
    """

    return measurement_raw_service.get_measurements(
        db=db,
        measurement_type=measurement_type,
        hive_level_id=hive_level_id,
        sensor_device_id=sensor_device_id,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )