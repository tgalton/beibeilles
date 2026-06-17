# =========================================================
# BASELINE AUTOMATIQUE
# =========================================================
#
# Représente une estimation automatique
# du niveau de référence de la balance.
#
# Exemple :
#
# L'algorithme détecte :
#
# - faible variance
# - faible pente
# - stabilité pendant 30 minutes
#
# Il estime alors :
#
# "La balance semble stable autour de
# 52.14 kg"
#
# Cette estimation devient une baseline.
#
# IMPORTANT :
#
# Une baseline n'est PAS une calibration.
#
# Elle représente uniquement une hypothèse
# calculée automatiquement.
#
# Une baseline pourra ensuite servir à
# générer une calibration automatique.
# =========================================================

from datetime import UTC
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class WeightBaseline(Base):
    __tablename__ = "weight_baselines"

    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_weight_baseline_confidence",
        ),
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
    # Une baseline correspond à une balance
    # précise.
    # =====================================================
    hive_level_id: Mapped[int] = mapped_column(
        ForeignKey("hive_levels.id"),
        nullable=False,
        index=True,
    )

    # =====================================================
    # Date à laquelle l'algorithme a produit
    # cette estimation.
    # =====================================================
    computed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    # =====================================================
    # Estimation de dérive calculée.
    #
    # Exemple :
    #
    # -2.35 kg
    #
    # Signifie :
    #
    # la balance semble décalée de 2.35 kg.
    # =====================================================
    baseline_offset_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =====================================================
    # Score de confiance.
    #
    # Exemple :
    #
    # 0.98
    #
    # Le score est calculé par l'algorithme
    # en fonction :
    #
    # - de la stabilité
    # - de la variance
    # - de la pente
    # - de la durée observée
    # =====================================================
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =====================================================
    # Durée de stabilité utilisée.
    #
    # Exemple :
    #
    # 30
    # 120
    # 360
    #
    # minutes
    #
    # Cette valeur aide à expliquer
    # le score de confiance obtenu.
    # =====================================================
    stable_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # =====================================================
    # Version de l'algorithme ayant généré
    # cette baseline.
    #
    # Exemple :
    #
    # v1
    # v2
    # v3
    # =====================================================
    algorithm_version: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    hive_level = relationship(
        "HiveLevel",
        back_populates="weight_baselines",
    )
