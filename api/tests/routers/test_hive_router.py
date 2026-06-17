from datetime import UTC
from datetime import datetime

from unittest.mock import Mock
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# =========================================================
# Fixture Hive
#
# On ajoute :
#
# - created_at
# - levels
#
# car HiveRead les exige.
#
# Sans ces champs FastAPI lèvera
# une ResponseValidationError.
# =========================================================
def fake_hive() -> dict:

    return {
        "id": 1,
        "name": "Ruche Alpha",
        "created_at": (
            datetime.now(
                UTC,
            ).isoformat()
        ),
        "levels": [],
    }


# =========================================================
# CREATE
# =========================================================
@patch(
    "app.services.hive_service.create_hive",
)
def test_create_hive(
    mock_create: Mock,
) -> None:

    mock_create.return_value = fake_hive()

    response = client.post(
        "/hives",
        json={
            "name": "Ruche Alpha",
        },
    )

    assert response.status_code == 200

    assert response.json()["name"] == "Ruche Alpha"


# =========================================================
# GET ALL
# =========================================================
@patch(
    "app.services.hive_service.get_hives",
)
def test_get_hives(
    mock_get: Mock,
) -> None:

    mock_get.return_value = [
        fake_hive(),
    ]

    response = client.get(
        "/hives",
    )

    assert response.status_code == 200

    assert len(response.json()) == 1


# =========================================================
# GET BY ID
# =========================================================
@patch(
    "app.services.hive_service.get_hive_by_id",
)
def test_get_hive_by_id(
    mock_get: Mock,
) -> None:

    mock_get.return_value = fake_hive()

    response = client.get(
        "/hives/1",
    )

    assert response.status_code == 200

    assert response.json()["id"] == 1


# =========================================================
# Vérifie transmission hive_id.
# =========================================================
@patch(
    "app.services.hive_service.get_hive_by_id",
)
def test_get_hive_by_id_passes_id(
    mock_get: Mock,
) -> None:

    mock_get.return_value = fake_hive()

    client.get(
        "/hives/42",
    )

    mock_get.assert_called_once()

    assert mock_get.call_args.kwargs["hive_id"] == 42


# =========================================================
# DELETE
# =========================================================
@patch(
    "app.services.hive_service.delete_hive",
)
def test_delete_hive(
    mock_delete: Mock,
) -> None:

    mock_delete.return_value = {
        "message": "Hive deleted",
    }

    response = client.delete(
        "/hives/1",
    )

    assert response.status_code == 200

    assert response.json()["message"] == "Hive deleted"


# =========================================================
# Vérifie transmission hive_id delete.
# =========================================================
@patch(
    "app.services.hive_service.delete_hive",
)
def test_delete_hive_passes_id(
    mock_delete: Mock,
) -> None:

    mock_delete.return_value = {
        "message": "Hive deleted",
    }

    client.delete(
        "/hives/123",
    )

    assert mock_delete.call_args.kwargs["hive_id"] == 123


# =========================================================
# UPDATE
# =========================================================
@patch(
    "app.services.hive_service.update_hive",
)
def test_update_hive(
    mock_update: Mock,
) -> None:

    hive = fake_hive()
    hive["name"] = "Ruche Beta"

    mock_update.return_value = hive

    response = client.put(
        "/hives/1",
        json={
            "name": "Ruche Beta",
        },
    )

    assert response.status_code == 200

    assert response.json()["name"] == "Ruche Beta"


# =========================================================
# Vérifie transmission paramètres update.
# =========================================================
@patch(
    "app.services.hive_service.update_hive",
)
def test_update_hive_passes_parameters(
    mock_update: Mock,
) -> None:

    mock_update.return_value = fake_hive()

    client.put(
        "/hives/5",
        json={
            "name": "Nouvelle ruche",
        },
    )

    mock_update.assert_called_once()

    assert mock_update.call_args.kwargs["hive_id"] == 5


# =========================================================
# Cas important :
#
# Vérifie que l'exception HTTP
# remonte correctement jusqu'au client.
#
# Ce test garantit que le contrat API
# reste stable :
#
# GET ruche inexistante
# => HTTP 404
# =========================================================
@patch(
    "app.services.hive_service.get_hive_by_id",
)
def test_get_hive_not_found(
    mock_get: Mock,
) -> None:

    mock_get.side_effect = HTTPException(
        status_code=404,
        detail="Hive not found",
    )

    response = client.get(
        "/hives/999",
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Hive not found"
