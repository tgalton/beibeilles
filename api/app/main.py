from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers.hive import router as hive_router
from app.routers.hive_level import router as hive_level_router
from app.routers.sensor_device import (
    router as sensor_device_router,
)
from app.routers.measurement_raw import (
    router as measurement_raw_router,
)
from app.routers.measurement_5m import (
    router as measurement_5m_router,
)
from app.routers.gateway_router import (
    router as gateway_router,
)
from app.routers import (
    measurement_corrected_router,
)

from app.database import engine
from app.database import wait_for_db


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("MAIN.PY LOADED")

    # WAIT FOR DB placé ici pour éviter de casser les tests py s'il est dans database (bloque mock)
    wait_for_db(engine)
    # =====================================================
    # Création automatique des tables SQLAlchemy
    # =====================================================

    yield


app = FastAPI(lifespan=lifespan)


# =========================================================
# Routers API
# =========================================================
app.include_router(hive_router)
app.include_router(hive_level_router)
app.include_router(sensor_device_router)
app.include_router(measurement_raw_router)
app.include_router(measurement_5m_router)
app.include_router(measurement_5m_router)
app.include_router(
    measurement_corrected_router.router,
)
app.include_router(gateway_router)


# =========================================================
# Route simple de test
# =========================================================
@app.get("/")
def root() -> dict[str, str]:

    return {
        "message": "Beehive API running",
    }
