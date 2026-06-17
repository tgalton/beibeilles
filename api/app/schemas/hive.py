from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import StrictStr

from app.schemas.hive_level import HiveLevelSimple


class HiveBase(BaseModel):
    name: StrictStr


class HiveCreate(HiveBase):
    pass


class HiveRead(HiveBase):
    id: int
    created_at: datetime

    levels: list[HiveLevelSimple] = []

    model_config = ConfigDict(from_attributes=True)


class HiveUpdate(BaseModel):
    name: str
