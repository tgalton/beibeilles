from unittest.mock import Mock
from unittest.mock import patch

import pytest

from fastapi import HTTPException

from app.services import hive_level_service
from app.schemas.hive_level import HiveLevelCreate


# =========================================================
# Fixture de niveau factice
#
# On utilise un dictionnaire simple car
# les services manipulent principalement
# les attributs attendus.
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
# Création d'un niveau
#
# Vérifie :
# - construction correcte du modèle
# - appel du repository
# =========================================================
@patch(
    "app.services.hive_level_service.hive_level_repository.create",
)
def test_create_hive_level(
    mock_create: Mock,
) -> None:

    expected = fake_hive_level()

    mock_create.return_value = expected

    hive_level = HiveLevelCreate(
        name="Corps",
        hive_id=10,
        lower_level_id=None,
        upper_level_id=2,
    )

    result = hive_level_service.create_hive_level(
        db=Mock(),
        hive_level=hive_level,
    )

    assert result == expected

    mock_create.assert_called_once()


# =========================================================
# Lecture de tous les niveaux
# =========================================================
@patch(
    "app.services.hive_level_service.hive_level_repository.get_all",
)
def test_get_hive_levels(
    mock_get_all: Mock,
) -> None:

    mock_get_all.return_value = [
        fake_hive_level(),
    ]

    result = hive_level_service.get_hive_levels(
        db=Mock(),
    )

    assert len(result) == 1

    mock_get_all.assert_called_once()


# =========================================================
# Lecture d'un niveau existant
# =========================================================
@patch(
    "app.services.hive_level_service.hive_level_repository.get_by_id",
)
def test_get_hive_level_by_id(
    mock_get_by_id: Mock,
) -> None:

    mock_get_by_id.return_value = fake_hive_level()

    result = hive_level_service.get_hive_level_by_id(
        db=Mock(),
        level_id=1,
    )

    assert result["id"] == 1

    mock_get_by_id.assert_called_once()


# =========================================================
# Niveau inexistant
#
# IMPORTANT :
# Cette exception constitue une vraie
# règle métier du service.
#
# Si elle disparaît un jour,
# ce test cassera immédiatement.
# =========================================================
@patch(
    "app.services.hive_level_service.hive_level_repository.get_by_id",
)
def test_get_hive_level_by_id_not_found(
    mock_get_by_id: Mock,
) -> None:

    mock_get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        hive_level_service.get_hive_level_by_id(
            db=Mock(),
            level_id=999,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Hive level not found"
