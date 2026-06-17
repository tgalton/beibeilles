from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class MeasurementRaw(Base):
    """
    =========================================================
    TABLE measurements_raw
    =========================================================

    Cette table contient les données BRUTES envoyées
    par les Raspberry.

    IMPORTANT :
    - aucune agrégation ici
    - aucune moyenne ici
    - aucune transformation ici

    Cette table est la source de vérité du système.

    Utilisation :
    - ingestion IoT
    - debug capteurs
    - récupération après perte réseau
    - recalcul futur d'agrégations

    ATTENTION :
    Cette table ne doit PAS être utilisée directement
    par Plotly pour les longues périodes.
    =========================================================
    """

    __tablename__ = "measurements_raw"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =========================================================
    # Type de mesure :
    # temperature / humidity / co2 / weight
    # =========================================================
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    # =========================================================
    # Valeur brute envoyée par le capteur
    # =========================================================
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =========================================================
    # Date réelle de la mesure
    # =========================================================
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # =========================================================
    # Device ayant envoyé la mesure
    # =========================================================
    sensor_device_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_devices.id"),
        nullable=False,
        index=True,
    )

    sensor_device = relationship(
        "SensorDevice",
        back_populates="measurements_raw",
    )

    # =========================================================
    # Niveau de ruche optionnel
    # Utilisé principalement pour les balances
    # =========================================================
    hive_level_id: Mapped[int | None] = mapped_column(
        ForeignKey("hive_levels.id"),
        nullable=True,
        index=True,
    )

    hive_level = relationship(
        "HiveLevel",
    )
