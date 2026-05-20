from datetime import datetime

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.sensor_device import SensorDevice
from app.repositories import sensor_device_repository
from app.schemas.iot_ingest import IoTIngest
from app.models.measurement import Measurement

from app.repositories import measurement_repository

from app.schemas.measurement import (
    MeasurementCreate,
)


def create_measurement(
    db: Session,
    measurement: MeasurementCreate,
):

    db_measurement = Measurement(
        type=measurement.type,
        value=measurement.value,
        measured_at=measurement.measured_at,
        sensor_device_id=measurement.sensor_device_id,
        hive_level_id=measurement.hive_level_id,
    )

    return measurement_repository.create(
        db=db,
        measurement=db_measurement,
    )


def get_measurements(
    db: Session,
    measurement_type: str | None = None,
    hive_level_id: int | None = None,
    sensor_device_id: int | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
):

    return measurement_repository.get_all(
        db=db,
        measurement_type=measurement_type,
        hive_level_id=hive_level_id,
        sensor_device_id=sensor_device_id,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )


def get_measurement_by_id(
    db: Session,
    measurement_id: int,
):

    measurement = measurement_repository.get_by_id(
        db=db,
        measurement_id=measurement_id,
    )

    if measurement is None:
        raise HTTPException(
            status_code=404,
            detail="Measurement not found",
        )

    return measurement

def ingest_measurements(
    db: Session,
    payload: IoTIngest,
) -> list[Measurement]:

    # =====================================================
    # 1. récupérer ou créer le device
    # =====================================================
    sensor_device: SensorDevice = (
        sensor_device_repository.get_or_create_by_serial(
            db=db,
            serial_number=payload.device_serial,
        )
    )

    created_measurements: list[Measurement] = []

    # =====================================================
    # 2. transformer payload -> ORM
    # =====================================================
    for m in payload.measurements:

        db_measurement = Measurement(
            type=m.type,
            value=m.value,
            hive_level_id=m.hive_level_id,
            sensor_device_id=sensor_device.id,
        )

        created_measurements.append(db_measurement)

    # =====================================================
    # 3. bulk insert
    # =====================================================
    return measurement_repository.create_many(
        db=db,
        measurements=created_measurements,
    )