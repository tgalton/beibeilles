from sqlalchemy.orm import Session

from fastapi import APIRouter
from fastapi import Depends

from app.database import get_db

from app.schemas.sensor_device import SensorDeviceCreate
from app.schemas.sensor_device import SensorDeviceRead

from app.services import sensor_device_service


router = APIRouter(
    prefix="/sensor-devices",
    tags=["SensorDevices"],
)


@router.post(
    "",
    response_model=SensorDeviceRead,
)
def create_sensor_device(
    sensor_device: SensorDeviceCreate,
    db: Session = Depends(get_db),
):
    return sensor_device_service.create_sensor_device(
        db=db,
        sensor_device=sensor_device,
    )