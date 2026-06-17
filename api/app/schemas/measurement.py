from datetime import UTC
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from typing import Literal


# =========================================================
# Types supportés par le système IoT
# =========================================================
MeasurementType = Literal[
    "temperature",
    "humidity",
    "co2",
    "weight",
]


class MeasurementBase(BaseModel):
    type: MeasurementType

    value: float

    hive_level_id: int | None = None

    # =========================================================
    # Date de mesure par défaut
    #
    # IMPORTANT :
    # default_factory attend UNE FONCTION
    # et non une valeur.
    #
    # Donc :
    # - MAUVAIS :
    #   datetime.now(UTC)
    #
    # - BON :
    #   lambda: datetime.now(UTC)
    #
    # Cela permet de générer une nouvelle date
    # à chaque création d'objet Pydantic.
    # =========================================================
    measured_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


# =========================================================
# Création API interne
# =========================================================
class MeasurementCreate(MeasurementBase):
    sensor_device_id: int


# =========================================================
# Lecture API
# =========================================================
class MeasurementRead(MeasurementBase):
    id: int

    sensor_device_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )
