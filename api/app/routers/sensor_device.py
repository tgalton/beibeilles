from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException
from fastapi import APIRouter
from fastapi import Depends

from api.app.models.sensor_device import SensorDevice
from api.app.repositories import sensor_device_repository
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
    db: Session,
    sensor_device: SensorDeviceCreate,
):

    db_sensor_device = SensorDevice(
        name=sensor_device.name,
        serial_number=sensor_device.serial_number,
        hive_id=sensor_device.hive_id,
    )

    try:

        return sensor_device_repository.create(
            db=db,
            sensor_device=db_sensor_device,
        )

    except IntegrityError:

        raise HTTPException(
            status_code=400,
            detail=(
                "Sensor device already exists "
                "or hive_id is invalid"
            ),
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
    return sensor_device_service.get_sensor_by_serial(
        db = db,
        serial_number = serial_number,
    )