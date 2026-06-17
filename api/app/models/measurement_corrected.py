from datetime import UTC
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database import Base


class MeasurementCorrected(Base):
    """
    =====================================================
    Poids corrigé après application
    d'une calibration.

    Une ligne représente :

        un Measurement5m
        +
        la calibration utilisée

    IMPORTANT :

    Les valeurs brutes ne sont jamais
    modifiées.

    Cette table contient uniquement
    le résultat du calcul.
    =====================================================
    """

    __tablename__ = "measurement_corrected"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # =====================================================
    # Bucket source.
    # =====================================================

    measurement_5m_id: Mapped[int] = mapped_column(
        ForeignKey(
            "measurements_5m.id",
        ),
        nullable=False,
        index=True,
        unique=True,
    )

    # =====================================================
    # Calibration utilisée.
    # =====================================================

    calibration_id: Mapped[int] = mapped_column(
        ForeignKey(
            "weight_calibrations.id",
        ),
        nullable=True,
        index=True,
    )
    # =====================================================
    # Poids brut moyen du bucket.
    # =====================================================

    raw_weight_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =====================================================
    # Poids corrigé.
    # =====================================================

    corrected_weight_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )