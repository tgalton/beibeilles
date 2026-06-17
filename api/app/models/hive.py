from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class Hive(Base):
    __tablename__ = "hives"

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

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
        nullable=False,
    )

    levels = relationship(
        "HiveLevel",
        back_populates="hive",
        cascade="all, delete-orphan",
    )

    sensor_devices = relationship(
        "SensorDevice",
        back_populates="hive",
        cascade="all, delete-orphan",
    )
