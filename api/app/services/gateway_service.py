# =========================================================
# app/services/gateway_service.py
# =========================================================

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.gateway import Gateway

from app.repositories import gateway_repository

from app.schemas.gateway import GatewayCreate

from app.services.gateway_secret_service import (
    generate_gateway_uid,
)
from app.services.gateway_secret_service import (
    generate_hmac_secret,
)


def create_gateway(
    db: Session,
    gateway_create: GatewayCreate,
) -> Gateway:
    """
    =========================================================
    Création d'une gateway.
    =========================================================

    Une gateway représente un Raspberry Pi.

    Lors de la création :

    - génération automatique du gateway_uid
    - génération automatique du secret HMAC

    =========================================================
    """

    gateway = Gateway(
        name=gateway_create.name,
        gateway_uid=generate_gateway_uid(),
        hmac_secret=generate_hmac_secret(),
    )

    return gateway_repository.create_gateway(
        db=db,
        gateway=gateway,
    )


def get_gateway_by_id(
    db: Session,
    gateway_id: int,
) -> Gateway:
    """
    Retourne une gateway.
    """

    gateway = gateway_repository.get_gateway_by_id(
        db=db,
        gateway_id=gateway_id,
    )

    if gateway is None:
        raise HTTPException(
            status_code=404,
            detail="Gateway not found",
        )

    return gateway


def get_gateway_by_uid(
    db: Session,
    gateway_uid: str,
) -> Gateway:
    """
    Recherche une gateway par UID.
    """

    gateway = gateway_repository.get_gateway_by_uid(
        db=db,
        gateway_uid=gateway_uid,
    )

    if gateway is None:
        raise HTTPException(
            status_code=404,
            detail="Gateway not found",
        )

    return gateway


def get_gateways(
    db: Session,
) -> list[Gateway]:
    """
    Retourne toutes les gateways.
    """

    return gateway_repository.get_gateways(
        db=db,
    )
