"""
=========================================================
CLEAN INTEGRATION TEST SETUP
=========================================================

✔ 1 transaction par test
✔ rollback automatique
✔ FastAPI utilise la même session DB
✔ zéro pollution entre tests
=========================================================
"""

import os
import pytest

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.dependencies.gateway_auth import authenticate_gateway

from tests.integration.fixtures.gateway_fixture import create_gateway
from tests.integration.fixtures.hive_fixture import create_hive_with_level
from tests.integration.fixtures.sensor_device_fixture import create_sensor_device


# =========================================================
# DATABASE TEST CONFIG
# =========================================================
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://beibeilles:beibeilles@localhost:5432/beibeilles"
)

engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# =========================================================
# TRANSACTION ISOLATION FIXTURE
# =========================================================
@pytest.fixture()
def db():
    """
    🔥 CORE IDEA :

    - on ouvre une transaction
    - tous les tests utilisent cette transaction
    - rollback automatique à la fin

    👉 donc aucune donnée ne persiste
    """

    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# =========================================================
# IMPORTANT : FASTAPI UTILISE LA MEME DB QUE LES TESTS
# =========================================================
@pytest.fixture(autouse=True)
def override_get_db(db):
    """
    🔥 CRITICAL FIX

    FastAPI endpoints utilisent EXACTEMENT la même session
    que les tests.

    👉 sinon :
    API commit = pollution DB = doublons
    """

    def _override():
        yield db

    app.dependency_overrides[get_db] = _override

    yield

    app.dependency_overrides.clear()


# =========================================================
# AUTH OVERRIDE
# =========================================================
@pytest.fixture(autouse=True)
def override_gateway_auth(db):
    """
    On bypass auth pour les tests API
    """

    gateway = create_gateway(db)

    def _override():
        return gateway

    app.dependency_overrides[authenticate_gateway] = _override

    yield

    app.dependency_overrides.clear()


# =========================================================
# CLIENT FASTAPI
# =========================================================
@pytest.fixture()
def client():
    return TestClient(app)


# =========================================================
# CONTEXTE SIMPLE (OPTIONNEL MAIS PROPRE)
# =========================================================
@pytest.fixture()
def integration_context(db):
    """
    Setup minimal cohérent pour tests complets
    """

    gateway = create_gateway(db)

    hive, hive_level = create_hive_with_level(db, gateway.id)

    sensor_device = create_sensor_device(db, hive.id)

    return {
        "gateway": gateway,
        "hive": hive,
        "hive_level": hive_level,
        "sensor_device": sensor_device,
    }