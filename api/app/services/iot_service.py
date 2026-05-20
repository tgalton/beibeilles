from sqlalchemy.orm import Session

from app.models.measurement import Measurement
from app.models.sensor_device import SensorDevice

from app.repositories import measurement_repository
from app.repositories import sensor_device_repository

from app.schemas.iot_ingest import IoTIngest


def ingest_measurements(
    db: Session,
    payload: IoTIngest,
) -> list[Measurement]:

    # =====================================================
    # Recherche ou création automatique
    # du device IoT
    # =====================================================
    sensor_device: SensorDevice = (
        sensor_device_repository
        .get_or_create_by_serial(
            db=db,
            serial_number=payload.device_serial,
        )
    )

    # =====================================================
    # Liste typée explicitement pour Pylance
    #
    # Sinon :
    # list[Unknown]
    # =====================================================
    measurements: list[Measurement] = []

    # =====================================================
    # Transformation payload Pydantic
    # -> modèles SQLAlchemy
    # =====================================================
    for measurement in payload.measurements:

        db_measurement = Measurement(

            type=measurement.type,

            value=measurement.value,

            hive_level_id=measurement.hive_level_id,

            sensor_device_id=sensor_device.id,
        )

        measurements.append(db_measurement)

    # =====================================================
    # Insertion batch SQL
    # =====================================================
    return measurement_repository.create_many(
        db=db,
        measurements=measurements,
    )