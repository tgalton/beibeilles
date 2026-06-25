# =========================================================
# app/models/gateway.py
# =========================================================

from datetime import UTC
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class Gateway(Base):
    """
    =========================================================
    Gateway IoT d'un rucher.
    =========================================================

    Une gateway correspond à un Raspberry Pi.

    Son rôle est de :
    - collecter les mesures des ESP32
    - transmettre les mesures vers l'API
    - signer les requêtes HTTP via HMAC
    - servir de point de confiance du rucher

    Relation métier :

        1 Gateway <-> N Hive

    Une gateway peut gérer plusieurs ruches.

    =========================================================
    Sécurité
    =========================================================

    gateway_uid :
        Identifiant public de la gateway.

    hmac_secret :
        Secret partagé entre le Raspberry
        et le backend.

    =========================================================
    """

    __tablename__ = "gateways"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    gateway_uid: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    hmac_secret: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    hives = relationship(
        "Hive",
        back_populates="gateway",
    )
