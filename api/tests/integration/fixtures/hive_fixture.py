from app.models.hive import Hive
from app.models.hive_level import HiveLevel


def create_hive_with_level(db, gateway_id: int):
    hive = Hive(
        name="Hive Test",
        gateway_id=gateway_id,
    )

    db.add(hive)
    db.flush()

    level = HiveLevel(
        name="body",
        hive_id=hive.id,
    )

    db.add(level)
    db.flush()

    return hive, level
