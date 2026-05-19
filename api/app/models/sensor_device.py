from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
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

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    serial_number: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    hive_id: Mapped[int] = mapped_column(
        ForeignKey("hives.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=(datetime.now(UTC)),
        nullable=False,
    )

    hive = relationship(
        "Hive",
        back_populates="sensor_devices",
    )
    
    measurements = relationship(
        "Measurement",
        back_populates="sensor_device",
    )