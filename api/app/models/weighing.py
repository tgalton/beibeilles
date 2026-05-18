from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class Weighing(Base):
    __tablename__ = "weighings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    measured_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    level_id: Mapped[int] = mapped_column(
        ForeignKey("hive_levels.id"),
        nullable=False,
    )

    level = relationship(
        "HiveLevel",
        back_populates="weighings",
    )
    
    sensor_device_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_devices.id"),
        nullable=False,
    )

    sensor_device = relationship(
        "SensorDevice",
    )