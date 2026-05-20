from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class HiveLevel(Base):
    __tablename__ = "hive_levels"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    hive_id: Mapped[int] = mapped_column(
        ForeignKey("hives.id"),
        nullable=False,
    )

    lower_level_id: Mapped[int | None] = mapped_column(
        ForeignKey("hive_levels.id"),
        nullable=True,
    )

    upper_level_id: Mapped[int | None] = mapped_column(
        ForeignKey("hive_levels.id"),
        nullable=True,
    )

    hive = relationship(
        "Hive",
        back_populates="levels",
    )

    lower_level = relationship(
        "HiveLevel",
        remote_side=[id],
        foreign_keys=[lower_level_id],
        post_update=True,
    )

    upper_level = relationship(
        "HiveLevel",
        remote_side=[id],
        foreign_keys=[upper_level_id],
        post_update=True,
    )
