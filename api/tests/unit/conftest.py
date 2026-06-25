import sys
from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parents[2]
print(ROOT_DIR)

# Pour éviter qu'à l'import app.database pytest retry 20 fois la connexion Postgresql :
os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@localhost:5432/test"

import pytest
from app.main import app
from app.dependencies.gateway_auth import authenticate_gateway
from app.models.gateway import Gateway

@pytest.fixture(autouse=True)
def override_gateway_auth():
    def _override():
        return Gateway(
            id=1,
            name="test-gateway",
            gateway_uid="test-gw",
            hmac_secret="test-secret",
            is_active=True,
        )

    app.dependency_overrides[authenticate_gateway] = _override

    yield

    app.dependency_overrides = {}


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
