from datetime import UTC
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.weight_reference_event import WeightReferenceEvent
from app.services import weight_reference_service
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

def apply_calibration(
    db: Session,
    hive_level_id: int,
    raw_weight: float,
    measured_at: datetime,
) -> float:
    """
    =========================================================
    Applique la calibration valide
    à la date de mesure.

    IMPORTANT :

    Les données brutes ne sont jamais
    modifiées.

    Cette méthode effectue uniquement
    le calcul métier.

    Formule :

    poids_corrige =
    (poids_brut - offset)
    × gain
    =========================================================
    """

    calibration = (
        weight_calibration_repository
        .get_for_datetime(
            db=db,
            hive_level_id=hive_level_id,
            measured_at=measured_at,
        )
    )

    if calibration is None:
        return raw_weight

    return (
        (
            raw_weight
            - calibration.offset_kg
        )
        * calibration.gain
    )


def create_calibration_from_reference_event(
    db: Session,
    reference_event: WeightReferenceEvent,
) -> WeightCalibration:
    """
    =====================================================
    Génère une calibration à partir d'un
    WeightReferenceEvent.
    =====================================================

    Exemple :

    poids attendu :
        1.000 kg

    poids observé :
        0.940 kg

    gain calculé :
        1.063829

    Processus :

    1) fermeture calibration active

    2) calcul du gain

    3) création nouvelle calibration

    IMPORTANT :

    Cette opération ne modifie pas
    l'offset.

    Seul le gain est recalculé.
    =====================================================
    """

    if not (
        weight_reference_service
        .is_reference_event_valid(
            expected_delta_kg=(
                reference_event.expected_delta_kg
            ),
            measured_delta_kg=(
                reference_event.measured_delta_kg
            ),
        )
    ):
        raise ValueError(
            "Invalid reference event"
        )

    gain = (
        weight_reference_service
        .compute_gain_from_reference(
            expected_delta_kg=(
                reference_event.expected_delta_kg
            ),
            measured_delta_kg=(
                reference_event.measured_delta_kg
            ),
        )
    )

    now = datetime.now(UTC)

    # =================================================
    # Ferme calibration actuelle
    # =================================================

    weight_calibration_repository\
        .close_current_calibration(
            db=db,
            hive_level_id=(
                reference_event.hive_level_id
            ),
            closed_at=now,
        )

    # =================================================
    # Nouvelle calibration
    # =================================================

    calibration = WeightCalibration(
        hive_level_id=(
            reference_event.hive_level_id
        ),
        valid_from=now,
        valid_to=None,

        # -----------------------------------------
        # Le poids étalon permet de recalculer
        # le gain mais pas le zéro.
        # -----------------------------------------
        offset_kg=0.0,

        gain=gain,

        source=(
            CalibrationSource
            .REFERENCE_WEIGHT
        ),
    )

    return (
        weight_calibration_repository
        .create(
            db=db,
            calibration=calibration,
        )
    )

def get_calibration_for_datetime(
    db: Session,
    hive_level_id: int,
    measured_at: datetime,
):
    """
    =====================================================
    Retourne la calibration valide
    pour une date donnée.
    =====================================================
    """

    return (
        weight_calibration_repository
        .get_for_datetime(
            db=db,
            hive_level_id=hive_level_id,
            measured_at=measured_at,
        )
    )