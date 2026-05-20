from pydantic import BaseModel

from typing import Literal


MeasurementType = Literal[
    "weight",
    "temperature",
    "humidity",
    "co2",
]


class IoTMeasurement(BaseModel):

    type: MeasurementType

    value: float

    hive_level_id: int | None = None


class IoTIngest(BaseModel):

    device_serial: str

    measurements: list[IoTMeasurement]