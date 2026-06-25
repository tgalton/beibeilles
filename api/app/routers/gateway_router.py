from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.gateway import GatewayCreate, GatewayProvisioningRead
from app.schemas.gateway import GatewayRead

from app.services import gateway_service


router = APIRouter(
    prefix="/gateways",
    tags=["Gateways"],
)


@router.post(
    "",
    # On retourne au post un gateway schéma spécifique avec le secret nécessaire qui ne sera disponible qu'à ce moment
    response_model=GatewayProvisioningRead,
)
def create_gateway(
    gateway_create: GatewayCreate,
    db: Session = Depends(get_db),
):
    """
    =========================================================
    Création d'une gateway.
    =========================================================

    Une gateway représente un Raspberry Pi
    associé à un rucher.

    Lors de la création :

    - un gateway_uid est généré
    - un hmac_secret est généré

    Le secret n'est jamais renvoyé par l'API.
    =========================================================
    """

    return gateway_service.create_gateway(
        db=db,
        gateway_create=gateway_create,
    )


@router.get(
    "",
    response_model=list[GatewayRead],
)
def get_gateways(
    db: Session = Depends(get_db),
):
    """
    =========================================================
    Liste toutes les gateways.
    =========================================================
    """

    return gateway_service.get_gateways(
        db=db,
    )


@router.get(
    "/{gateway_id}",
    response_model=GatewayRead,
)
def get_gateway(
    gateway_id: int,
    db: Session = Depends(get_db),
):
    """
    =========================================================
    Retourne une gateway par son identifiant.
    =========================================================
    """

    return gateway_service.get_gateway_by_id(
        db=db,
        gateway_id=gateway_id,
    )
