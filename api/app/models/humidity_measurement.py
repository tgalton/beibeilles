from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class HumidityMeasurement(Base):
    __tablename__ = "humidity_measurements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    humidity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    measured_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    sensor_device_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_devices.id"),
        nullable=False,
    )

    sensor_device = relationship(
        "SensorDevice",
        back_populates="humidity_measurements",
    )