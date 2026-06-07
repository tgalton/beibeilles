from unittest.mock import Mock
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# =========================================================
# Fixture fake hive level
#
# Doit respecter exactement
# le schéma HiveLevelRead.
# =========================================================
def fake_hive_level() -> dict:

    return {
        "id": 1,
        "name": "Corps",
        "hive_id": 10,
        "lower_level_id": None,
        "upper_level_id": 2,
    }


# =========================================================
# Création niveau
# =========================================================
@patch(
    "app.services.hive_level_service.create_hive_level",
)
def test_create_hive_level(
    mock_create: Mock,
) -> None:

    mock_create.return_value = fake_hive_level()

    response = client.post(
        "/hive-levels",
        json={
            "name": "Corps",
            "hive_id": 10,
            "lower_level_id": None,
            "upper_level_id": 2,
        },
    )

    assert response.status_code == 200

    assert response.json()["name"] == "Corps"


# =========================================================
# Lecture d'un niveau
# =========================================================
@patch(
    "app.services.hive_level_service.get_hive_level_by_id",
)
def test_get_hive_level(
    mock_get: Mock,
) -> None:

    mock_get.return_value = fake_hive_level()

    response = client.get(
        "/hive-levels/1",
    )

    assert response.status_code == 200

    assert response.json()["id"] == 1


# =========================================================
# Vérification transmission ID
#
# Test très utile :
# il garantit que le router transmet
# correctement les paramètres URL.
# =========================================================
@patch(
    "app.services.hive_level_service.get_hive_level_by_id",
)
def test_get_hive_level_passes_id(
    mock_get: Mock,
) -> None:

    mock_get.return_value = fake_hive_level()

    client.get(
        "/hive-levels/123",
    )

    mock_get.assert_called_once()

    assert (
        mock_get.call_args.kwargs["level_id"]
        == 123
    )


# =========================================================
# Lecture liste niveaux
# =========================================================
@patch(
    "app.services.hive_level_service.get_hive_levels",
)
def test_get_hive_levels(
    mock_get: Mock,
) -> None:

    mock_get.return_value = [
        fake_hive_level(),
    ]

    response = client.get(
        "/hive-levels",
    )

    assert response.status_code == 200

    assert len(response.json()) == 1


# =========================================================
# Gestion erreur métier
#
# Ici on vérifie que FastAPI convertit
# correctement l'HTTPException du service
# en réponse HTTP.
# =========================================================
@patch(
    "app.services.hive_level_service.get_hive_level_by_id",
)
def test_get_hive_level_not_found(
    mock_get: Mock,
) -> None:

    mock_get.side_effect = HTTPException(
        status_code=404,
        detail="Hive level not found",
    )

    response = client.get(
        "/hive-levels/999",
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "Hive level not found"
    )