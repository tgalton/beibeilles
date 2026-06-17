from pydantic import BaseModel
from pydantic import ConfigDict


class HiveLevelBase(BaseModel):
    name: str
    hive_id: int
    lower_level_id: int | None = None
    upper_level_id: int | None = None


class HiveLevelCreate(HiveLevelBase):
    pass


class HiveLevelRead(HiveLevelBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HiveLevelSimple(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)
