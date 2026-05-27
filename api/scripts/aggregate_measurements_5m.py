from app.database import SessionLocal

from app.services.measurement_aggregation_service import (
    aggregate_measurements_5m,
)


def main() -> None:
    """
    =========================================================
    Lance l'agrégation 5 minutes.
    =========================================================
    """

    db = SessionLocal()

    try:

        aggregate_measurements_5m(
            db=db,
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()