from sqlalchemy.orm import Session

from app.models.weighing import Weighing

from datetime import datetime


def create(
    db: Session,
    weighing: Weighing,
) -> Weighing:
    db.add(weighing)

    db.commit()

    db.refresh(weighing)

    return weighing


def get_all(
    db: Session,
    level_id: int | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
) -> list[Weighing]:

    query = db.query(Weighing)

    if level_id is not None:
        query = query.filter(
            Weighing.level_id == level_id,
        )

    if start_at is not None:
        query = query.filter(
            Weighing.measured_at >= start_at,
        )

    if end_at is not None:
        query = query.filter(
            Weighing.measured_at <= end_at,
        )

    query = query.order_by(
        Weighing.measured_at.desc(),
    )

    query = query.limit(limit)

    return query.all()


def get_by_id(
    db: Session,
    weighing_id: int,
) -> Weighing | None:
    return (
        db.query(Weighing)
        .filter(Weighing.id == weighing_id)
        .first()
    )