from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi import Depends
from datetime import UTC
from datetime import datetime

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.gateway import Gateway

from app.repositories import gateway_repository

from app.services import gateway_service
from app.services import gateway_auth_service


async def authenticate_gateway(
    request: Request,
    db: Session = Depends(get_db),
    x_gateway_uid: str = Header(
        alias="X-Gateway-Uid",
    ),
    x_timestamp: str = Header(
        alias="X-Timestamp",
    ),
    x_signature: str = Header(
        alias="X-Signature",
    ),
) -> Gateway:
    """
    =========================================================
    Authentification HMAC des gateways.
    =========================================================
    """

    gateway = gateway_service.get_gateway_by_uid(
        db=db,
        gateway_uid=x_gateway_uid,
    )

    if not gateway.is_active:
        raise HTTPException(
            status_code=403,
            detail="Gateway disabled",
        )

    if not gateway_auth_service.validate_timestamp(
        x_timestamp,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid timestamp",
        )

    body = await request.body()

    if not gateway_auth_service.verify_signature(
        secret=gateway.hmac_secret,
        timestamp=x_timestamp,
        body=body,
        received_signature=x_signature,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature",
        )

    gateway.last_seen_at = datetime.now(UTC)

    gateway_repository.update_gateway(
        db=db,
        gateway=gateway,
    )

    return gateway
