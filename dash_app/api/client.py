from pathlib import Path
from typing import Any

import pandas as pd
import requests
import os
from datetime import datetime

from dotenv import load_dotenv



# =========================================================
# Dossier courant du projet Dash
# =========================================================
BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# Sélection environnement
# =========================================================
if "API_URL" not in os.environ:
    load_dotenv()
API_URL = os.environ["API_URL"]

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
    start_at: datetime | None = None,
    end_at: datetime | None = None,
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
        
    if start_at is not None:
        params["start_at"] = start_at.isoformat()

    if end_at is not None:
        params["end_at"] = end_at.isoformat()

    response = requests.get(
        f"{API_URL}/measurements/5m",
        params=params,
    )

    print("URL =", response.url)
    print("STATUS =", response.status_code)
    print("TEXT =", response.text[:500])

    response.raise_for_status()

    data = response.json()

    print("JSON TYPE =", type(data))

    df = pd.DataFrame(data)

    print(df.head())
    print(df.columns)

    return df