from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.schemas.iot_ingest import IoTIngest

from app.repositories import sensor_device_repository

from app.models.weighing import Weighing

from app.models.temperature_measurement import (
    TemperatureMeasurement,
)

from app.models.humidity_measurement import (
    HumidityMeasurement,
)

from app.models.co2_measurement import (
    CO2Measurement,
)


def ingest_measurements(
    db: Session,
    payload: IoTIngest,
):

    sensor_device = (
        sensor_device_repository.get_by_serial(
            db=db,
            serial_number=payload.device_serial,
        )
    )

    if sensor_device is None:
        raise HTTPException(
            status_code=404,
            detail="Sensor device not found",
        )

    created_measurements = []

    for measurement in payload.measurements:

        if measurement.type == "weight":

            if measurement.hive_level is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Weight measurement "
                        "requires hive_level"
                    ),
                )

            db_measurement = Weighing(
                weight=measurement.value,
                level_id=measurement.hive_level,
                sensor_device_id=sensor_device.id,
            )

        elif measurement.type == "temperature":

            db_measurement = TemperatureMeasurement(
                temperature=measurement.value,
                sensor_device_id=sensor_device.id,
            )

        elif measurement.type == "humidity":

            db_measurement = HumidityMeasurement(
                humidity=measurement.value,
                sensor_device_id=sensor_device.id,
            )

        elif measurement.type == "co2":

            db_measurement = CO2Measurement(
                co2=measurement.value,
                sensor_device_id=sensor_device.id,
            )

        else:
            continue

        db.add(db_measurement)

        created_measurements.append(db_measurement)

    db.commit()

    return {
        "message": "Measurements ingested",
        "count": len(created_measurements),
    }