# =========================================================
# CALIBRATION APPLIQUEE
# =========================================================
#
# Représente une correction réellement utilisée
# pour calculer le poids affiché.
#
# Exemple :
#
# offset = -2.4 kg
#
# poids_corrige =
# poids_mesure - offset
#
# Une calibration peut provenir :
#
# - d'une action manuelle
# - d'un poids de référence
# - d'une dérive détectée automatiquement
#
# IMPORTANT :
#
# Contrairement à WeightBaseline,
# une calibration modifie effectivement
# le calcul du poids affiché.
#
# Les calibrations sont historisées
# afin de permettre le recalcul complet
# des données corrigées.
# =========================================================

from datetime import UTC
from datetime import datetime

from app.enums.calibration_source import CalibrationSource
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Enum
from sqlalchemy import CheckConstraint

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


from app.database import Base

class WeightCalibration(Base):
    __tablename__ = "weight_calibrations"

    __table_args__ = (
        # Les dates de validé ont un ordre
        CheckConstraint(
            "valid_to IS NULL OR valid_to > valid_from",
            name="ck_weight_calibration_dates",
        ),
        # L'event de calibration passe toujours par un ajout de masse
        CheckConstraint(
            "gain > 0",
            name="ck_weight_calibration_gain_positive",
        )
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =====================================================
    # Niveau concerné.
    #
    # IMPORTANT :
    # Une calibration est appliquée
    # à une balance précise.
    # =====================================================
    hive_level_id: Mapped[int] = mapped_column(
        ForeignKey("hive_levels.id"),
        nullable=False,
        index=True,
    )

    # =====================================================
    # Début de validité.
    # =====================================================
    valid_from: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    # =====================================================
    # Fin de validité.
    #
    # NULL :
    #
    # calibration actuellement active.
    # =====================================================
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    
    # =====================================================
    # Décalage appliqué.
    #
    # poids_corrige =
    # poids_mesure - offset
    # =====================================================
    offset_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =====================================================
    # Facteur multiplicatif.
    #
    # poids_corrige =
    #
    # (poids_mesure - offset)
    # * gain
    #
    # Valeur par défaut :
    #
    # 1.0
    # =====================================================
    gain: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    # =====================================================
    # Origine de la calibration.
    #
    # Exemple :
    #
    # manual
    # auto_drift
    # reference_weight
    # =====================================================


    source: Mapped[CalibrationSource] = mapped_column(
        Enum(
            CalibrationSource,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    # =====================================================
    # Version de l'algorithme.
    #
    # Utile pour retracer l'origine
    # exacte d'une correction.
    # =====================================================
    algorithm_version: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # =====================================================
    # Event ayant conduit à cette calibration.
    #
    # Exemple :
    #
    # calibration calculée à partir
    # d'un poids étalon.
    #
    # Permet la traçabilité complète.
    #
    # NULL :
    #
    # calibration manuelle
    # ou ancienne calibration.
    # =====================================================
    reference_event_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "weight_reference_events.id",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    hive_level = relationship(
        "HiveLevel",
        back_populates="weight_calibrations",
    )

    reference_event = relationship(
        "WeightReferenceEvent",
    )