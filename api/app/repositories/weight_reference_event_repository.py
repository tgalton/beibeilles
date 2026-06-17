from app.models.weight_reference_event import (
    WeightReferenceEvent,
)

from sqlalchemy.orm import Session


# create()
def create(
    db: Session,
    event: WeightReferenceEvent,
) -> WeightReferenceEvent:

    db.add(event)

    db.commit()

    db.refresh(event)

    return event


# get_by_id()
def get_by_id(
    db: Session,
    event_id: int,
) -> WeightReferenceEvent | None:

    return (
        db.query(
            WeightReferenceEvent,
        )
        .filter(
            WeightReferenceEvent.id == event_id,
        )
        .first()
    )


# Récupérer la dernière référence
def get_latest_for_hive_level(
    db: Session,
    hive_level_id: int,
) -> WeightReferenceEvent | None:
    """
    =====================================================
    Retourne le dernier événement de référence
    enregistré pour une balance.
    =====================================================
    """

    return (
        db.query(WeightReferenceEvent)
        .filter(
            WeightReferenceEvent.hive_level_id == hive_level_id,
        )
        .order_by(
            WeightReferenceEvent.created_at.desc(),
        )
        .first()
    )
