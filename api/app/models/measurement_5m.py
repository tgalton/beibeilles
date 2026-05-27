from datetime import UTC
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class Measurement5m(Base):
    """
    =========================================================
    Données agrégées 5 minutes.
    =========================================================

    IMPORTANT :
    Cette table est utilisée par :
    - Plotly
    - dashboards
    - analytics

    Elle contient des données déjà réduites.

    Le but :
    éviter d'interroger les millions de lignes RAW.
    =========================================================
    """

    __tablename__ = "measurements_5m"

    # =====================================================
    # IMPORTANT :
    #
    # Un bucket 5m doit être UNIQUE pour :
    #
    # - 1 timestamp bucket
    # - 1 type
    # - 1 hive
    # - 1 sensor
    # - 1 hive_level
    #
    # Cela évite :
    # - doublons
    # - double agrégation
    # - corruption silencieuse
    # =====================================================
    __table_args__ = (
        UniqueConstraint(
            "bucket_at",
            "type",
            "hive_id",
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

    # =====================================================
    # Début du bucket 5 minutes
    #
    # Exemple :
    # 14:05:00
    # =====================================================
    bucket_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # =====================================================
    # Type de mesure :
    # temperature / humidity / co2 / weight
    # =====================================================
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    # =====================================================
    # Ruche résolue au moment de l'agrégation.
    #
    # IMPORTANT :
    # le RAW n'a PAS hive_id.
    #
    # Cela permet :
    # - branchement plug and play
    # - association hive après coup
    # - historique récupérable
    # =====================================================
    hive_id: Mapped[int] = mapped_column(
        ForeignKey("hives.id"),
        nullable=True,
        index=True,
    )

    # =====================================================
    # Device source
    # =====================================================
    sensor_device_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_devices.id"),
        nullable=False,
        index=True,
    )

    # =====================================================
    # Niveau de ruche éventuel
    # =====================================================
    hive_level_id: Mapped[int | None] = mapped_column(
        ForeignKey("hive_levels.id"),
        nullable=True,
        index=True,
    )

    # =====================================================
    # Valeurs statistiques
    # =====================================================
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

    # =====================================================
    # Nombre d'échantillons RAW
    # ayant servi à produire ce bucket.
    # =====================================================
    samples_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # =====================================================
    # Relations SQLAlchemy
    # =====================================================
    sensor_device = relationship(
        "SensorDevice",
        back_populates="measurements_5m",
    )

    hive = relationship(
        "Hive",
    )

    hive_level = relationship(
        "HiveLevel",
    )