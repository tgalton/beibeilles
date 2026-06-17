from datetime import UTC
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.sensor_device import SensorDevice


# =========================================================
# Création d'un SensorDevice
# =========================================================
def create(
    db: Session,
    sensor_device: SensorDevice,
) -> SensorDevice:

    db.add(sensor_device)

    db.commit()

    db.refresh(sensor_device)

    return sensor_device


# =========================================================
# Recherche par serial
# =========================================================
def get_by_serial(
    db: Session,
    serial_number: str,
) -> SensorDevice | None:

    return (
        db.query(SensorDevice)
        .filter(
            SensorDevice.serial_number == serial_number,
        )
        .first()
    )


# =========================================================
# Liste complète des devices
# =========================================================
def get_all(
    db: Session,
) -> list[SensorDevice]:

    return db.query(SensorDevice).all()


# =========================================================
# Recherche ou création automatique
#
# Utilisé par l'ingestion IoT :
# - si le device existe déjà :
#     -> mise à jour du last_seen_at
# - sinon :
#     -> création automatique
# =========================================================
def get_or_create_by_serial(
    db: Session,
    serial_number: str,
) -> SensorDevice:

    device = get_by_serial(
        db=db,
        serial_number=serial_number,
    )

    # =====================================================
    # Device déjà connu
    # =====================================================
    if device is not None:
        device.last_seen_at = datetime.now(UTC)

        db.commit()

        db.refresh(device)

        return device

    # =====================================================
    # Nouveau device détecté
    # =====================================================
    device = SensorDevice(
        name=f"Auto device {serial_number}",
        serial_number=serial_number,
        is_registered=False,
        created_at=datetime.now(UTC),
        last_seen_at=datetime.now(UTC),
    )

    db.add(device)

    db.commit()

    db.refresh(device)

    return device
