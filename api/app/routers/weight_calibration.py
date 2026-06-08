from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.weight_calibration import (
    WeightCalibrationCreate,
)
from app.schemas.weight_calibration import (
    WeightCalibrationRead,
)

from app.services import (
    weight_calibration_service,
)


router = APIRouter(
    prefix="/weight-calibrations",
    tags=["Weight Calibrations"],
)


@router.post(
    "/manual",
    response_model=WeightCalibrationRead,
)
def create_manual_calibration(
    payload: WeightCalibrationCreate,
    db: Session = Depends(get_db),
):
    """
    =========================================================
    Création manuelle d'une calibration.

    Exemple :

    offset = -2.4 kg

    signifie :

    la balance dérive actuellement
    de -2.4 kg.
    =========================================================
    """

    return (
        weight_calibration_service
        .create_manual_calibration(
            db=db,
            payload=payload,
        )
    )