# =========================================================
# app/repositories/gateway_repository.py
# =========================================================

from sqlalchemy.orm import Session

from app.models.gateway import Gateway


def create_gateway(
    db: Session,
    gateway: Gateway,
) -> Gateway:
    """
    Sauvegarde une gateway.
    """

    db.add(gateway)
    db.commit()
    db.refresh(gateway)

    return gateway


def get_gateway_by_id(
    db: Session,
    gateway_id: int,
) -> Gateway | None:
    """
    Recherche une gateway par son identifiant.
    """

    return (
        db.query(Gateway)
        .filter(Gateway.id == gateway_id)
        .first()
    )


def get_gateway_by_uid(
    db: Session,
    gateway_uid: str,
) -> Gateway | None:
    """
    Recherche une gateway à partir de son UID.
    """

    return (
        db.query(Gateway)
        .filter(
            Gateway.gateway_uid == gateway_uid,
        )
        .first()
    )


def get_gateways(
    db: Session,
) -> list[Gateway]:
    """
    Retourne toutes les gateways.
    """

    return db.query(Gateway).all()


def update_gateway(
    db: Session,
    gateway: Gateway,
) -> Gateway:
    """
    Persiste les modifications.
    """

    db.commit()
    db.refresh(gateway)

    return gateway


def delete_gateway(
    db: Session,
    gateway: Gateway,
) -> None:
    """
    Supprime une gateway.
    """

    db.delete(gateway)
    db.commit()