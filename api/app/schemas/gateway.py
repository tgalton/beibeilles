# =========================================================
# app/schemas/gateway.py
# =========================================================

from datetime import datetime

from pydantic import BaseModel


class GatewayCreate(BaseModel):
    """
    Création d'une gateway.
    """

    name: str


class GatewayRead(BaseModel):
    """
    Lecture d'une gateway.
    """

    id: int

    name: str

    gateway_uid: str

    is_active: bool

    created_at: datetime

    last_seen_at: datetime | None

    model_config = {
        "from_attributes": True,
    }


class GatewayProvisioningRead(BaseModel):
    """
    Réponse utilisée uniquement lors du provisioning.

    Le secret HMAC est renvoyé une seule fois.
    """

    id: int

    name: str

    gateway_uid: str

    hmac_secret: str

    is_active: bool

    model_config = {
        "from_attributes": True,
    }