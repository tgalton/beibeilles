from datetime import UTC
from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from typing import Literal


MeasurementType = Literal[
    "temperature",
    "humidity",
    "co2",
    "weight",
]


class IoTMeasurement(BaseModel):

    # =====================================================
    # Type de donnée IoT
    # =====================================================
    type: MeasurementType

    # =====================================================
    # Valeur brute mesurée
    # =====================================================
    value: float

    # =====================================================
    # Niveau de ruche associé
    # =====================================================
    hive_level_id: int | None = None

    # =====================================================
    # Timestamp réel du Raspberry
    #
    # IMPORTANT :
    # permet :
    # - buffer offline
    # - resynchronisation réseau
    # - conservation temporelle exacte
    #
    # Fallback :
    # UTC serveur
    # =====================================================
    measured_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


class IoTIngest(BaseModel):

    device_serial: str

    measurements: list[IoTMeasurement]