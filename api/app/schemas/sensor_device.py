from datetime import datetime
from pydantic import ConfigDict
from pydantic import BaseModel


class SensorDeviceCreate(BaseModel):
    name: str

    serial_number: str


class SensorDeviceRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    name: str

    serial_number: str

    hive_id: int

    created_at: datetime
