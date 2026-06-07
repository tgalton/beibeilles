import os

from collections.abc import Generator

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_fixed


# =========================================================
# Chargement du fichier .env
#
# IMPORTANT :
# En Docker :
# les variables d'environnement Docker
# écrasent automatiquement celles du .env
#
# En local :
# Python utilisera le fichier .env
# =========================================================
if "DATABASE_URL" not in os.environ:
    load_dotenv()


# =========================================================
# URL de connexion PostgreSQL / TimescaleDB
#
# IMPORTANT :
# Il n'y a PLUS de fallback SQLite.
#
# Ca évite :
# - environnements incohérents
# - comportements SQL différents
# - migrations cassées
# - bugs impossibles à reproduire
# =========================================================
DATABASE_URL: str | None = os.getenv(
    "DATABASE_URL",
)
if DATABASE_URL is None:
    raise RuntimeError(
        "DATABASE_URL environment variable is required",
    )

# =========================================================
# Base SQLAlchemy
#
# Tous les modèles héritent de Base.
#
# SQLAlchemy utilise Base.metadata
# pour connaître automatiquement
# toutes les tables du projet.
# =========================================================
class Base(DeclarativeBase):
    pass


# =========================================================
# Création du moteur SQLAlchemy
#
# Le moteur représente :
# - la connexion PostgreSQL
# - le pool de connexions
# - la configuration SQLAlchemy
#
# pool_pre_ping=True :
#
# vérifie automatiquement
# qu'une connexion SQL est encore valide
# avant de l'utiliser.
#
# Très utile avec :
# - Docker
# - redémarrages DB
# - connexions longues
# =========================================================
def create_db_engine() -> Engine:

    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )


# =========================================================
# Instance globale du moteur SQLAlchemy
# =========================================================
engine = create_db_engine()


# =========================================================
# Attente que PostgreSQL soit disponible
#
# IMPORTANT :
# Avec Docker Compose,
# l'API peut démarrer AVANT PostgreSQL.
#
# Tenacity retry automatiquement :
# - 20 tentatives
# - toutes les 2 secondes
# =========================================================
@retry(
    stop=stop_after_attempt(20),
    wait=wait_fixed(2),
)
def wait_for_db(
    engine: Engine,
) -> None:

    # =====================================================
    # Tentative réelle de connexion SQL
    #
    # Si PostgreSQL n'est pas prêt :
    # exception -> retry automatique
    # =====================================================
    with engine.connect():

        print("Database connection established.")

        return


# =========================================================
# Factory de sessions SQLAlchemy
#
# Une Session représente :
# - une unité de travail SQL
# - les transactions
# - les requêtes
# =========================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# =========================================================
# Dependency FastAPI
#
# Fournit automatiquement
# une session DB par requête HTTP.
#
# FastAPI :
# - ouvre la session
# - l'injecte dans le endpoint
# - ferme automatiquement la session
# =========================================================
def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()