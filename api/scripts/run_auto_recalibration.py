from app.database import SessionLocal

from app.repositories import (
    hive_level_repository,
)

from app.services import (
    auto_recalibration_orchestrator,
)


def main() -> None:
    """
    =====================================================
    Lance l'auto recalibration sur toutes les ruches.
    =====================================================
    """

    db = SessionLocal()

    try:
        hive_levels = hive_level_repository.get_all(
            db=db,
        )

        print(f"[AUTO RECALIBRATION] {len(hive_levels)} hive levels found")

        for hive_level in hive_levels:
            print(f"[AUTO RECALIBRATION] processing hive_level={hive_level.id}")

            auto_recalibration_orchestrator.run(
                db=db,
                hive_level_id=hive_level.id,
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
