from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from app.database import Base


class Measurement5m(Base):
    """
    =========================================================
    TABLE measurements_5m
    =========================================================

    Cette table contient les données agrégées
    toutes les 5 minutes.

    IMPORTANT :
    - utilisée UNIQUEMENT pour le dashboard
    - utilisée UNIQUEMENT pour Plotly

    Les données ici sont déjà résumées.

    Exemple :
    - moyenne du poids
    - minimum
    - maximum

    Cette table réduit énormément le nombre de points.
    =========================================================
    """

    __tablename__ = "measurements_5m"
    
    __table_args__ = (
        UniqueConstraint(
            "bucket_at",
            "type",
            "sensor_device_id",
            "hive_level_id",
            name="uq_measurement_5m_bucket",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    bucket_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    avg_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    min_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    max_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    samples_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    sensor_device_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_devices.id"),
        nullable=False,
        index=True,
    )
    
    sensor_device = relationship(
        "SensorDevice",
        back_populates="measurements_5m",
    )

    hive_level_id: Mapped[int | None] = mapped_column(
        ForeignKey("hive_levels.id"),
        nullable=True,
        index=True,
    )