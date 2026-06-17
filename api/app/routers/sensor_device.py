from sqlalchemy.orm import Session

from fastapi import APIRouter
from fastapi import Depends

from app.database import get_db

from app.models.sensor_device import SensorDevice

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
) -> SensorDevice:

    return sensor_device_service.create_sensor_device(
        db=db,
        sensor_device=sensor_device,
    )


@router.get(
    "",
    response_model=list[SensorDeviceRead],
)
def get_all_sensor(
    db: Session = Depends(get_db),
) -> list[SensorDevice]:

    return sensor_device_service.get_sensor_all_device(
        db=db,
    )


@router.get(
    "/{serial_number}",
    response_model=SensorDeviceRead,
)
def get_sensor(
    serial_number: str,
    db: Session = Depends(get_db),
) -> SensorDevice:

    return sensor_device_service.get_sensor_by_serial(
        db=db,
        serial_number=serial_number,
    )


@router.post(
    "/{serial_number}/associate-hive/{hive_id}",
    response_model=SensorDeviceRead,
)
def associate_hive(
    serial_number: str,
    hive_id: int,
    db: Session = Depends(get_db),
) -> SensorDevice:

    return sensor_device_service.associate_device_with_hive(
        db=db,
        serial_number=serial_number,
        hive_id=hive_id,
    )
