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

    # =====================================================
    # Recherche ou création automatique
    # du device IoT
    # =====================================================
    sensor_device: SensorDevice = sensor_device_repository.get_or_create_by_serial(
        db=db,
        serial_number=payload.device_serial,
    )

    # =====================================================
    # Liste typée explicitement pour Pylance
    #
    # Sinon :
    # list[Unknown]
    # =====================================================
    measurements: list[MeasurementRaw] = []

    # =====================================================
    # Transformation payload Pydantic
    # -> modèles SQLAlchemy
    # =====================================================
    for measurement in payload.measurements:
        db_measurement = MeasurementRaw(
            # =============================================
            # Type de mesure :
            # temperature / humidity / co2 / weight
            # =============================================
            type=measurement.type,
            # =============================================
            # Valeur brute du capteur
            # =============================================
            value=measurement.value,
            # =============================================
            # Niveau de ruche associé
            # (optionnel)
            # =============================================
            hive_level_id=measurement.hive_level_id,
            # =============================================
            # Device IoT ayant envoyé la mesure
            # =============================================
            sensor_device_id=sensor_device.id,
            # =============================================
            # IMPORTANT :
            #
            # On utilise le timestamp envoyé
            # par le Raspberry si présent.
            #
            # Cela permet :
            # - buffer offline
            # - resynchronisation réseau
            # - conservation du vrai timestamp
            #
            # Fallback :
            # heure serveur UTC
            # =============================================
            measured_at=(measurement.measured_at or datetime.now(UTC)),
        )

        measurements.append(db_measurement)

    # =====================================================
    # Insertion batch SQL
    #
    # IMPORTANT :
    # un seul commit SQL
    # pour optimiser les performances
    # IoT.
    # =====================================================
    return measurement_raw_repository.create_many(
        db=db,
        measurements=measurements,
    )
