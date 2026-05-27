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

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("MAIN.PY LOADED")

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



# =========================================================
# Route simple de test
# =========================================================
@app.get("/")
def root() -> dict[str, str]:

    return {
        "message": "Beehive API running",
    }