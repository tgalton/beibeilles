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


class SensorDevice(Base):
    __tablename__ = "sensor_devices"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =====================================================
    # Nom humain modifiable
    # =====================================================
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # =====================================================
    # Identifiant matériel unique
    #
    # Exemple :
    # A0B7651F92CC
    # =====================================================
    serial_number: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    # =====================================================
    # Device auto enregistré ou validé
    # par un utilisateur/admin
    # =====================================================
    is_registered: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # =====================================================
    # Dernière communication connue
    # =====================================================
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    measurements = relationship(
        "Measurement",
        back_populates="sensor_device",
    )