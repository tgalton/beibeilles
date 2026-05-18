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

# Create
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
    
# GetAllSensors
@router.get(
    "",
    response_model=list[SensorDeviceRead],
)
def get_all_sensor(
    db: Session = Depends(get_db),
):
    return sensor_device_service.get_sensor_all_device(db=db)

# GetBySerial
@router.get(
    "/{serial_number}",
    response_model= SensorDeviceRead)
def get_sensor(
    serial_number: str,
    db : Session = Depends(get_db),
):
    return sensor_device_service.get_sensor(
        db = db,
        serial_number = serial_number,
    )