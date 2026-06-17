from datetime import UTC
from datetime import datetime
from datetime import timedelta

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.measurement_raw import MeasurementRaw


def delete_old_raw_measurements(
    db: Session,
    retention_days: int = 7,
) -> int:
    """
    =========================================================
    Suppression des anciennes mesures RAW.
    =========================================================

    OBJECTIF :
    éviter que la table RAW grossisse indéfiniment.

    IMPORTANT :
    les données RAW sont temporaires.

    Les dashboards utilisent :
    - measurement_5m

    Donc :
    après agrégation,
    les RAW anciennes peuvent être supprimées.

    =========================================================
    Stratégie :
    =========================================================

    On supprime toutes les données :

        measured_at < now - retention_days

    Exemple :
    retention_days = 7

    => suppression des données > 7 jours

    =========================================================
    Pourquoi garder quelques jours ?
    =========================================================

    Cela permet :
    - buffer Raspberry offline
    - debug capteur
    - reprocessing éventuel
    - vérification agrégation

    =========================================================
    Retour :
    =========================================================

    Nombre de lignes supprimées.
    =========================================================
    """

    # =====================================================
    # Calcul de la date limite
    # =====================================================
    cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)

    print(f"[RAW CLEANUP] cutoff_date={cutoff_date.isoformat()}")

    # =====================================================
    # Requête DELETE SQLAlchemy moderne
    #
    # synchronize_session=False :
    # beaucoup plus rapide pour les bulk delete
    # =====================================================
    statement = delete(MeasurementRaw).where(
        MeasurementRaw.measured_at < cutoff_date,
    )

    db.execute(statement)

    db.commit()

    deleted_count = 0

    print(f"[RAW CLEANUP] deleted_rows={deleted_count}")

    return deleted_count


def main() -> None:
    """
    =========================================================
    Point d'entrée script CLI.
    =========================================================

    Ce script est destiné à être exécuté :
    - manuellement
    - via cron
    - via docker exec

    Exemple :

    docker exec beibeilles-api \
        python scripts/delete_raw_after_7days.py
    =========================================================
    """

    db = SessionLocal()

    try:
        print("[RAW CLEANUP] starting cleanup...")

        deleted_count = delete_old_raw_measurements(
            db=db,
            retention_days=7,
        )

        print(f"[RAW CLEANUP] completed (deleted={deleted_count})")

    except Exception as e:
        print(f"[RAW CLEANUP] ERROR: {e}")

        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
