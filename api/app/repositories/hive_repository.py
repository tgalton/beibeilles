from sqlalchemy.orm import Session

from app.models.hive import Hive


def create(
    db: Session,
    name: str,
) -> Hive:
    hive = Hive(
        name=name,
    )

    db.add(hive)

    db.commit()

    db.refresh(hive)

    return hive


def get_all(
    db: Session,
) -> list[Hive]:
    return db.query(Hive).all()


def get_by_id(
    db: Session,
    hive_id: int,
) -> Hive | None:
    return db.query(Hive).filter(Hive.id == hive_id).first()


def delete(
    db: Session,
    hive: Hive,
) -> None:
    db.delete(hive)

    db.commit()


def update(
    db: Session,
    hive: Hive,
) -> Hive:
    db.commit()

    db.refresh(hive)

    return hive
