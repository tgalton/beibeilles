from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.hive import Hive
from app.models.sensor_device import SensorDevice

from app.repositories import sensor_device_repository

from app.schemas.sensor_device import (
    SensorDeviceCreate,
)


# =========================================================
# Création d'un device
# =========================================================
def create_sensor_device(
    db: Session,
    sensor_device: SensorDeviceCreate,
) -> SensorDevice:

    db_sensor_device = SensorDevice(
        name=sensor_device.name,
        serial_number=sensor_device.serial_number,
    )

    return sensor_device_repository.create(
        db=db,
        sensor_device=db_sensor_device,
    )


# =========================================================
# Récupération de tous les devices
# =========================================================
def get_sensor_all_device(
    db: Session,
) -> list[SensorDevice]:

    return sensor_device_repository.get_all(
        db=db,
    )


# =========================================================
# Recherche par serial
# =========================================================
def get_sensor_by_serial(
    db: Session,
    serial_number: str,
) -> SensorDevice:

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


def get_or_create_by_serial(
    db: Session,
    serial_number: str,
) -> SensorDevice:

    device = (
        db.query(SensorDevice)
        .filter(SensorDevice.serial_number == serial_number)
        .first()
    )

    if device:
        return device

    device = SensorDevice(
        name=f"Device {serial_number}",
        serial_number=serial_number,
        # Pas de ruche id associé dans ce cas : association à faire plus tard
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def associate_device_with_hive(
    db: Session,
    serial_number: str,
    hive_id: int,
) -> SensorDevice:

    # =====================================================
    # 1. Récupération du device
    # =====================================================
    sensor = sensor_device_repository.get_by_serial(
        db=db,
        serial_number=serial_number,
    )

    if sensor is None:
        raise HTTPException(
            status_code=404,
            detail="Sensor device not found",
        )

    # =====================================================
    # 2. Vérification hive existe
    # =====================================================
    hive = db.query(Hive).filter(Hive.id == hive_id).first()

    if hive is None:
        raise HTTPException(
            status_code=404,
            detail="Hive not found",
        )

    # =====================================================
    # 3. Association
    # =====================================================
    sensor.hive_id = hive_id

    db.add(sensor)
    db.commit()
    db.refresh(sensor)

    return sensor
