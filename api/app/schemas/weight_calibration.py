from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict

from app.enums.calibration_source import (
    CalibrationSource,
)


class WeightCalibrationCreate(
    BaseModel,
):
    """
    =========================================================
    Création manuelle d'une calibration.
    =========================================================
    """

    hive_level_id: int

    offset_kg: float

    gain: float = 1.0


class WeightCalibrationRead(
    BaseModel,
):
    """
    =========================================================
    Représentation API d'une calibration.
    =========================================================
    """

    id: int

    hive_level_id: int

    valid_from: datetime

    valid_to: datetime | None

    offset_kg: float

    gain: float

    source: CalibrationSource

    algorithm_version: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )