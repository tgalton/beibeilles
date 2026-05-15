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


def get_weighings(level_id: int | None = None):
    """
    Récupère les pesées depuis l'API.

    level_id :
        - permet de filtrer par ruche
        - optionnel
    """

    params = {}

    # Si une ruche est sélectionnée → filtre API
    if level_id is not None:
        params["level_id"] = level_id

    response = requests.get(
        f"{API_URL}/weighings",
        params=params,
    )

    response.raise_for_status()

    data = response.json()

    # Transformation en DataFrame pour Plotly
    return pd.DataFrame(data)