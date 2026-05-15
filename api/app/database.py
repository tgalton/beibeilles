from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_fixed

import os
import time

DATABASE_URL = os.getenv("DATABASE_URL", "")


# ========================================================
# Base SQLAlchemy
# =========================================================
# Tous les modèles hériteront de cette classe.
# SQLAlchemy utilisera Base.metadata
# pour connaître toutes les tables.
# ========================================================
class Base(DeclarativeBase):
    pass


# ========================================================
# IMPORTANT 
# on importe les modèles APRÈS Base
# pour éviter les imports circulaires
# =========================================================
import app.models


# ========================================================
# Création du moteur PostgreSQL
# =========================================================
def create_db_engine():
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )


engine = create_db_engine()


# ========================================================
# Attente que PostgreSQL soit prêt
# (utile avec Docker Compose)
# =========================================================
@retry(
    stop=stop_after_attempt(20),
    wait=wait_fixed(2),
)
def wait_for_db(engine):
    for _ in range(30):
        try:
            with engine.connect():
                return

        except Exception:
            time.sleep(2)


wait_for_db(engine)


# =========================================================
# Factory de sessions SQLAlchemy
# ========================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ========================================================
# Dependency FastAPI
# Fournit une session DB par requête HTTP
# =========================================================
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()