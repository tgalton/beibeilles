from uuid import uuid4
from app.models.gateway import Gateway


def create_gateway(db):
    obj = Gateway(
        name="integration-gateway",
        gateway_uid=f"gw-{uuid4()}",
        hmac_secret="secret",
        is_active=True,
    )

    db.add(obj)
    db.flush()  # ❌ PAS commit

    return obj