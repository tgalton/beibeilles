from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.sensor_device import SensorDeviceCreate
from app.models.sensor_device import SensorDevice

from app.repositories import sensor_device_repository


# Create Device
def create_sensor_device(
    db: Session,
    sensor_device: SensorDeviceCreate,
) -> SensorDevice:

    db_sensor_device = SensorDevice(
        name=sensor_device.name,
        serial_number=sensor_device.serial_number,
        hive_id=sensor_device.hive_id,
    )

    try:

        db.add(db_sensor_device)

        db.commit()

        db.refresh(db_sensor_device)

        return db_sensor_device

    except IntegrityError:

        db.rollback()

        raise
    
# GetAll 
def get_sensor_all_device(
    db: Session,
):
    return sensor_device_repository.get_all(db=db)


def get_sensor_by_serial(
    db: Session,
    serial_number: str,
):
    sensor = sensor_device_repository.get_by_serial(
        db=db,
        serial_number=serial_number,
    )

    if sensor is None:
        raise HTTPException(
            status_code=404,
            detail="Sensor not found",
        )

    return sensor