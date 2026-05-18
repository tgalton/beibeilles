from sqlalchemy.orm import Session

from app.models.sensor_device import SensorDevice


def create(
    db: Session,
    sensor_device: SensorDevice,
) -> SensorDevice:

    db.add(sensor_device)

    db.commit()

    db.refresh(sensor_device)

    return sensor_device


def get_by_serial(
    db: Session,
    serial_number: str,
) -> SensorDevice | None:

    return (
        db.query(SensorDevice)
        .filter(
            SensorDevice.serial_number == serial_number
        )
        .first()
    )