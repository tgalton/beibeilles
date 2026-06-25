from uuid import uuid4
from app.models.sensor_device import SensorDevice


def create_sensor_device(db, hive_id: int):
    obj = SensorDevice(
        name="ESP32",
        serial_number=f"ESP32-{uuid4()}",
        is_registered=True,
        hive_id=hive_id,
    )

    db.add(obj)
    db.flush()

    return obj