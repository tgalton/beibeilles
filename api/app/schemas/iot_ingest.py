from pydantic import BaseModel

from typing import Literal


class IoTMeasurement(BaseModel):

    type: Literal[
        "weight",
        "temperature",
        "humidity",
        "co2",
    ]

    value: float

    hive_level: int | None = None


class IoTIngest(BaseModel):

    device_serial: str

    measurements: list[IoTMeasurement]