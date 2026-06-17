# =========================================================
# EVENEMENT DE REFERENCE
# =========================================================
#
# Représente une action volontaire de l'utilisateur.
#
# Exemple :
#
# L'apiculteur pose un poids étalon de 1 kg
# sur la balance.
#
# Le système mesure :
#
# +0.94 kg
#
# alors qu'il attendait :
#
# +1.00 kg
#
# Cet événement permet :
#
# - d'évaluer la qualité de calibration
# - de recalculer un gain
# - d'ancrer les algorithmes automatiques
#
# IMPORTANT :
#
# Un WeightReferenceEvent ne corrige rien.
#
# Il enregistre uniquement un fait observé.
# =========================================================

from datetime import UTC
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


class WeightReferenceEvent(Base):
    __tablename__ = "weight_reference_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =====================================================
    # Niveau de ruche concerné
    #
    # IMPORTANT :
    # La calibration est réalisée sur une balance
    # précise et non sur l'ensemble de la ruche.
    #
    # Chaque hausse / corps peut posséder sa propre
    # cellule de charge.
    # =====================================================
    hive_level_id: Mapped[int] = mapped_column(
        ForeignKey("hive_levels.id"),
        nullable=False,
        index=True,
    )

    # =====================================================
    # Variation attendue.
    #
    # Exemple :
    #
    # l'utilisateur pose un poids étalon de :
    #
    # +1.000 kg
    # =====================================================
    expected_delta_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =====================================================
    # Variation réellement observée.
    #
    # Exemple :
    #
    # +0.942 kg
    # =====================================================
    measured_delta_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =====================================================
    # Commentaire libre.
    #
    # Exemple :
    #
    # "Poids étalon certifié 1kg"
    # "Test annuel"
    # =====================================================
    comment: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # =====================================================
    # Relation SQLAlchemy
    # =====================================================
    hive_level = relationship(
        "HiveLevel",
        back_populates="weight_reference_events",
    )
