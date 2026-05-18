from datetime import datetime

from pydantic import BaseModel


class SensorDeviceCreate(BaseModel):

    name: str

    serial_number: str

    hive_id: int


class SensorDeviceRead(BaseModel):

    id: int

    name: str

    serial_number: str

    hive_id: int

    created_at: datetime

    class Config:
        from_attributes = True