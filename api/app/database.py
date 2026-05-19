import os

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_fixed

from dotenv import load_dotenv


# =========================================================
# Chargement du fichier .env
#
# En développement local :
# Python lira automatiquement :
#
# DATABASE_URL=sqlite:///./beehive.db
#
# En Docker / production :
# les variables d'environnement Docker
# écraseront celles du .env.
# =========================================================
load_dotenv()


# =========================================================
# URL de connexion SQLAlchemy
#
# Fallback :
# SQLite local si DATABASE_URL n'existe pas.
# =========================================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./beehive.db",
)


# =========================================================
# Base SQLAlchemy
#
# Tous les modèles hériteront de Base.
#
# SQLAlchemy utilisera Base.metadata
# pour connaître automatiquement
# toutes les tables du projet.
# =========================================================
class Base(DeclarativeBase):
    pass


# =========================================================
# Création du moteur SQLAlchemy
#
# Le moteur représente :
# - la connexion à la DB
# - le pool de connexions
# - la configuration SQLAlchemy
#
# IMPORTANT :
# SQLite nécessite :
#
# check_same_thread=False
#
# car FastAPI peut utiliser plusieurs threads.
# =========================================================
def create_db_engine() -> Engine:

    # =====================================================
    # Cas SQLite local
    # =====================================================
    if DATABASE_URL.startswith("sqlite"):

        return create_engine(
            DATABASE_URL,

            # =================================================
            # SQLite interdit par défaut
            # les accès multi-threads.
            #
            # FastAPI pouvant utiliser plusieurs threads,
            # on désactive cette protection.
            # =================================================
            connect_args={
                "check_same_thread": False,
            },

            pool_pre_ping=True,
        )

    # =====================================================
    # Cas PostgreSQL / TimescaleDB
    # =====================================================
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
# Utile surtout avec Docker Compose :
#
# - le container API peut démarrer
#   avant PostgreSQL
#
# Tenacity retry automatiquement :
# - 20 tentatives
# - toutes les 2 secondes
# =========================================================
@retry(
    stop=stop_after_attempt(20),
    wait=wait_fixed(2),
)
def wait_for_db(engine: Engine) -> None:

    # =====================================================
    # SQLite est un simple fichier local.
    #
    # Il est toujours disponible immédiatement.
    #
    # Donc inutile d'attendre.
    # =====================================================
    if DATABASE_URL.startswith("sqlite"):
        return

    # =====================================================
    # PostgreSQL :
    # tentative réelle de connexion.
    #
    # Si échec :
    # exception => retry Tenacity
    # =====================================================
    with engine.connect():
        return


wait_for_db(engine)


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