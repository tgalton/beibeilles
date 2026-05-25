from datetime import UTC
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.measurement_raw import MeasurementRaw
from app.models.sensor_device import SensorDevice

from app.repositories import measurement_raw_repository
from app.repositories import sensor_device_repository

from app.schemas.iot_ingest import IoTIngest


def ingest_measurements(
    db: Session,
    payload: IoTIngest,
) -> list[MeasurementRaw]:
    """
    =========================================================
    Ingestion des mesures IoT.

    IMPORTANT :
    Cette fonction ne fait QUE :
    - transformer le payload
    - stocker les données RAW

    Aucun calcul d'agrégation ici.

    Pourquoi ?

    Parce que l'ingestion doit rester :
    - rapide
    - simple
    - robuste

    L'agrégation sera faite plus tard
    par un job dédié.
    =========================================================
    """
    # =====================================================
    # 1. récupérer ou créer le device
    # =====================================================
    sensor_device: SensorDevice = (
        sensor_device_repository.get_or_create_by_serial(
            db=db,
            serial_number=payload.device_serial,
        )
    )

    created_measurements: list[MeasurementRaw] = []
    
    # =====================================================
    # 2. transformer payload -> ORM
    # =====================================================

    for m in payload.measurements:

        db_measurement = MeasurementRaw(
            type=m.type,
            value=m.value,
            hive_level_id=m.hive_level_id,
            sensor_device_id=sensor_device.id,

            # =============================================
            # IMPORTANT :
            #
            # on utilise le timestamp du capteur
            # si disponible.
            #
            # sinon fallback serveur.
            # =============================================
            measured_at=m.measured_at or datetime.now(UTC),
        )

        created_measurements.append(db_measurement)

    # =====================================================
    # 3. bulk insert
    # =====================================================
    return measurement_raw_repository.create_many(
        db=db,
        measurements=created_measurements,
    )