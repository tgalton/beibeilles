from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class WeighingBase(BaseModel):
    weight: float
    level_id: int
    measured_at: datetime = Field(
        default_factory=datetime.utcnow,
    )

class WeighingCreate(WeighingBase):
    pass


class WeighingRead(WeighingBase):
    id: int
    measured_at: datetime

    model_config = ConfigDict(from_attributes=True)