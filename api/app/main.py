from fastapi import FastAPI

from app.database import Base
from app.database import engine

from app.routers.hive import router as hive_router
from app.routers.hive_level import router as hive_level_router
from app.routers.weighing import router as weighing_router

app = FastAPI()


# =========================================================
# Routers API
# =========================================================

app.include_router(hive_router)
app.include_router(hive_level_router)
app.include_router(weighing_router)


# =========================================================
# Startup application
# =========================================================
# Création automatique des tables SQLAlchemy
# au démarrage de l'API.
# =========================================================
@app.on_event("startup")
def startup():

    Base.metadata.create_all(bind=engine)


# =========================================================
# Route simple de test
# =========================================================
@app.get("/")
def root() -> dict[str, str]:

    return {
        "message": "Beehive API running",
    }