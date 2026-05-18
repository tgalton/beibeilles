from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.sensor_device import SensorDevice

from app.repositories import sensor_device_repository

from app.schemas.sensor_device import SensorDeviceCreate

# Create Device
def create(
    db: Session,
    sensor_device: SensorDevice,
) -> SensorDevice:

    try:
        db.add(sensor_device)

        db.commit()

        db.refresh(sensor_device)

        return sensor_device

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