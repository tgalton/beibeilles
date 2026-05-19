from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import Base, engine

from app.routers.hive import router as hive_router
from app.routers.hive_level import router as hive_level_router
from app.routers.sensor_device import (
    router as sensor_device_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # =========================================================
    # Startup application
    # =========================================================
    Base.metadata.create_all(bind=engine)

    yield

    # =========================================================
    # Shutdown application
    # =========================================================
    # Rien pour le moment


app = FastAPI(lifespan=lifespan)


# =========================================================
# Routers API
# =========================================================

app.include_router(hive_router)
app.include_router(hive_level_router)
app.include_router(sensor_device_router)


# =========================================================
# Route simple de test
# =========================================================
@app.get("/")
def root() -> dict[str, str]:

    return {
        "message": "Beehive API running",
    }