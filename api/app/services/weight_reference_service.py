from sqlalchemy.orm import Session

from app.models.weight_reference_event import (
    WeightReferenceEvent,
)

from app.repositories import (
    weight_reference_event_repository,
)


# =========================================================
# SERVICE POIDS ETALON
# =========================================================
#
# Ce service centralise toute la logique métier
# liée aux poids de référence.
#
# Exemple :
#
# L'apiculteur place un poids étalon de :
#
# +1.000 kg
#
# La balance mesure :
#
# +0.942 kg
#
# Cela signifie que la balance sous-estime
# légèrement les variations de poids.
#
# Le système peut alors calculer :
#
# gain = 1.000 / 0.942
#
# afin de corriger les futures mesures.
#
# IMPORTANT :
#
# Un WeightReferenceEvent n'applique
# aucune correction.
#
# Il enregistre uniquement une observation
# terrain exploitable ultérieurement.
# =========================================================


def create_reference_event(
    db: Session,
    hive_level_id: int,
    expected_delta_kg: float,
    measured_delta_kg: float,
    comment: str | None = None,
) -> WeightReferenceEvent:
    """
    =====================================================
    Enregistre un nouvel événement de référence.
    =====================================================

    Exemple :

    poids étalon :
        +1.000 kg

    variation observée :
        +0.942 kg

    Le système conserve cet événement afin
    d'alimenter les futurs calculs
    de calibration.

    IMPORTANT :

    Aucun recalibrage n'est réalisé ici.
    """

    event = WeightReferenceEvent(
        hive_level_id=hive_level_id,
        expected_delta_kg=expected_delta_kg,
        measured_delta_kg=measured_delta_kg,
        comment=comment,
    )

    return (
        weight_reference_event_repository
        .create(
            db=db,
            event=event,
        )
    )


def compute_gain_from_reference(
    expected_delta_kg: float,
    measured_delta_kg: float,
) -> float:
    """
    =====================================================
    Calcule le gain théorique à appliquer.
    =====================================================

    Exemple :

    poids attendu :
        1.000 kg

    poids mesuré :
        0.942 kg

    gain :
        1.000 / 0.942
        = 1.06157

    Cela signifie :

    toutes les variations de poids
    devront être multipliées par
    environ 1.06.

    IMPORTANT :

    Le gain peut être :

    > 1
        balance qui sous-estime

    < 1
        balance qui surestime

    = 1
        balance parfaitement calibrée
    =====================================================
    """

    if measured_delta_kg == 0:
        raise ValueError(
            "measured_delta_kg cannot be zero",
        )

    return (
        expected_delta_kg
        / measured_delta_kg
    )


def is_reference_event_valid(
    expected_delta_kg: float,
    measured_delta_kg: float,
) -> bool:
    """
    =====================================================
    Vérification métier minimale.
    =====================================================

    Un poids étalon doit toujours produire
    une variation du même signe.

    Exemple valide :

        +1.0 kg
        +0.95 kg

    Exemple invalide :

        +1.0 kg
        -0.95 kg

    Cela indiquerait probablement :

    - erreur de manipulation
    - capteur défectueux
    - câblage incorrect
    =====================================================
    """

    return (
        expected_delta_kg
        * measured_delta_kg
    ) > 0



def get_latest_reference_event(
    db: Session,
    hive_level_id: int,
) -> WeightReferenceEvent | None:
    """
    =====================================================
    Retourne le dernier événement de référence
    enregistré pour une balance.

    Cet événement représente le dernier test
    réalisé avec un poids étalon.

    Exemple :

    2026-06-01 :
        +1.000 kg attendu
        +0.942 kg mesuré

    Ce type d'information permet :

    - d'évaluer la dérive réelle
    - de recalculer un gain
    - de suivre le vieillissement
      des cellules de charge

    Retour :

        WeightReferenceEvent

    ou

        None

    si aucun test n'a encore été réalisé.
    =====================================================
    """

    return (
        weight_reference_event_repository
        .get_latest_for_hive_level(
            db=db,
            hive_level_id=hive_level_id,
        )
    )