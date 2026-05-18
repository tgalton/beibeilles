from sqlalchemy.orm import Session

from app.models.sensor_device import SensorDevice

from app.repositories import sensor_device_repository

from app.schemas.sensor_device import SensorDeviceCreate


def create_sensor_device(
    db: Session,
    sensor_device: SensorDeviceCreate,
):

    db_sensor_device = SensorDevice(
        name=sensor_device.name,
        serial_number=sensor_device.serial_number,
        hive_id=sensor_device.hive_id,
    )

    return sensor_device_repository.create(
        db=db,
        sensor_device=db_sensor_device,
    )