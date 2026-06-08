from datetime import UTC
from datetime import datetime

from sqlalchemy.orm import Session

from app.enums.calibration_source import (
    CalibrationSource,
)

from app.models.weight_calibration import (
    WeightCalibration,
)

from app.repositories import (
    weight_calibration_repository,
)

from app.schemas.weight_calibration import (
    WeightCalibrationCreate,
)


def create_manual_calibration(
    db: Session,
    payload: WeightCalibrationCreate,
) -> WeightCalibration:
    """
    =========================================================
    Crée une calibration manuelle.

    IMPORTANT :

    Avant de créer la nouvelle calibration :

    - on ferme l'ancienne
    - on conserve l'historique

    Ceci garantit qu'il n'existe jamais
    plusieurs calibrations actives pour
    une même balance.
    =========================================================
    """

    now = datetime.now(UTC)

    weight_calibration_repository.close_current_calibration(
        db=db,
        hive_level_id=payload.hive_level_id,
        closed_at=now,
    )

    calibration = WeightCalibration(
        hive_level_id=payload.hive_level_id,

        valid_from=now,

        valid_to=None,

        offset_kg=payload.offset_kg,

        gain=payload.gain,

        source=CalibrationSource.MANUAL,

        algorithm_version=None,
    )

    return weight_calibration_repository.create(
        db=db,
        calibration=calibration,
    )


def get_current_calibration(
    db: Session,
    hive_level_id: int,
) -> WeightCalibration | None:
    """
    =========================================================
    Retourne la calibration active.

    Cette méthode sera utilisée plus tard
    par le moteur de correction du poids.
    =========================================================
    """

    return (
        weight_calibration_repository
        .get_current_for_hive_level(
            db=db,
            hive_level_id=hive_level_id,
        )
    )