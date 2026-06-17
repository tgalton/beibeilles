from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import (
    get_db,
)

from app.services import (
    corrected_weight_query_service,
)


router = APIRouter(
    prefix="/measurements/corrected",
    tags=["Measurements Corrected"],
)



@router.get("")
def get_corrected_measurements(
    hive_level_id: int,
    start_at: datetime,
    end_at: datetime,
    db: Session = Depends(get_db),
):
    """
    =====================================================
    Historique des poids corrigés.

    Endpoint destiné principalement
    au dashboard Plotly.
    =====================================================
    """

    return (
        corrected_weight_query_service
        .get_weight_history(
            db=db,
            hive_level_id=hive_level_id,
            start_at=start_at,
            end_at=end_at,
        )
    )


@router.get("/latest")
def get_latest_corrected_weight(
    hive_level_id: int,
    db: Session = Depends(get_db),
):
    """
    =====================================================
    Dernier poids corrigé disponible.
    =====================================================
    """

    return (
        corrected_weight_query_service
        .get_latest_weight(
            db=db,
            hive_level_id=hive_level_id,
        )
    )