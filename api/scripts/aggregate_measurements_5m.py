from app.database import SessionLocal

from app.services.measurement_aggregation_service import (
    aggregate_measurements_5m,
)


def main() -> None:
    """
    =========================================================
    Script d'agrégation des mesures RAW
    vers la table measurement_5m.
    =========================================================

    Ce script est exécuté périodiquement
    via cron/docker.

    IMPORTANT :
    il ne doit JAMAIS être appelé
    depuis les endpoints FastAPI.
    =========================================================
    """

    db = SessionLocal()

    try:

        print("Starting 5m aggregation...")

        aggregate_measurements_5m(
            db=db,
        )

        print("5m aggregation completed.")

    finally:

        db.close()


if __name__ == "__main__":
    main()