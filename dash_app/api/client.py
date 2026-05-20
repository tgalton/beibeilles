import requests
import pandas as pd

# URL interne Docker (service FastAPI)
API_URL = "http://api:8000"


def get_hives():
    """
    Récupère la liste des ruches depuis l'API FastAPI.
    """

    response = requests.get(f"{API_URL}/hives")

    # Si erreur HTTP → exception automatique
    response.raise_for_status()

    return response.json()


def get_measurements(
    hive_level_id: int | None = None,
    sensor_device_id: int | None = None,
    measurement_type: str | None = None,
):
    """
    Récupère les measurements depuis l'API.
    """

    params = {}

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

    return pd.DataFrame(response.json())