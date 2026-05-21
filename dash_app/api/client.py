from pathlib import Path
from typing import Any

import pandas as pd
import requests
import os

from dotenv import load_dotenv



# =========================================================
# Dossier courant du projet Dash
# =========================================================
BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# Sélection environnement
# =========================================================
ENV = os.getenv(
    "APP_ENV",
    "local",
)


# =========================================================
# Chargement du bon fichier .env
# =========================================================
if ENV == "docker":

    load_dotenv(
        BASE_DIR / ".env.docker",
    )

else:

    load_dotenv(
        BASE_DIR / ".env.local",
    )


# =========================================================
# URL API FastAPI
# =========================================================
API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000",
)

# =========================================================
# Récupération des ruches
# =========================================================
def get_hives() -> list[dict[str, Any]]:
    """
    Appelle l'API FastAPI pour récupérer
    toutes les ruches.
    """

    response = requests.get(f"{API_URL}/hives")

    # Déclenche une exception automatique
    # si status HTTP != 2xx
    response.raise_for_status()

    return response.json()


# =========================================================
# Récupération des measurements
# =========================================================
def get_measurements(
    hive_level_id: int | None = None,
    sensor_device_id: int | None = None,
    measurement_type: str | None = None,
) -> pd.DataFrame:
    """
    Récupère les mesures depuis l'API
    puis les convertit en DataFrame pandas.
    """

    params: dict[str, int | str] = {}

    # -----------------------------------------------------
    # Construction dynamique des query params
    # -----------------------------------------------------
    if hive_level_id is not None:
        params["hive_level_id"] = hive_level_id

    if sensor_device_id is not None:
        params["sensor_device_id"] = sensor_device_id

    if measurement_type is not None:
        params["measurement_type"] = measurement_type

    response = requests.get(
        f"{API_URL}/measurements",
        params=params,
    )

    response.raise_for_status()

    # -----------------------------------------------------
    # Conversion JSON -> DataFrame pandas
    # -----------------------------------------------------
    return pd.DataFrame(response.json())