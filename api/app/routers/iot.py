from sqlalchemy.orm import Session

from fastapi import APIRouter
from fastapi import Depends

from app.database import get_db

from app.schemas.iot_ingest import IoTIngest

from app.services import iot_service


router = APIRouter(
    prefix="/iot",
    tags=["IoT"],
)


@router.post("/ingest")
def ingest_measurements(
    payload: IoTIngest,
    db: Session = Depends(get_db),
):
    return iot_service.ingest_measurements(
        db=db,
        payload=payload,
    )