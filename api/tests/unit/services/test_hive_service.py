from unittest.mock import Mock
from unittest.mock import patch

from fastapi import HTTPException

from app.services import hive_service


# =========================================================
# Fixture Hive simulée
#
# On utilise un dictionnaire simple car
# le repository sera entièrement mocké.
#
# Cela permet de tester uniquement
# la logique métier du service.
# =========================================================
def fake_hive() -> dict:

    return {
        "id": 1,
        "name": "Ruche Alpha",
    }


# =========================================================
# CREATE
#
# Vérifie que le service délègue bien
# la création au repository.
# =========================================================
@patch(
    "app.repositories.hive_repository.create",
)
def test_create_hive(
    mock_create: Mock,
) -> None:

    mock_create.return_value = fake_hive()

    hive = Mock()
    hive.name = "Ruche Alpha"

    result = hive_service.create_hive(
        db=Mock(),
        hive=hive,
    )

    assert result["name"] == "Ruche Alpha"


# =========================================================
# Vérifie transmission du nom.
# =========================================================
@patch(
    "app.repositories.hive_repository.create",
)
def test_create_hive_passes_name(
    mock_create: Mock,
) -> None:

    hive = Mock()
    hive.name = "Ruche Alpha"

    hive_service.create_hive(
        db=Mock(),
        hive=hive,
    )

    mock_create.assert_called_once()

    assert mock_create.call_args.kwargs["name"] == "Ruche Alpha"


# =========================================================
# GET ALL
# =========================================================
@patch(
    "app.repositories.hive_repository.get_all",
)
def test_get_hives(
    mock_get_all: Mock,
) -> None:

    mock_get_all.return_value = [
        fake_hive(),
    ]

    result = hive_service.get_hives(
        db=Mock(),
    )

    assert len(result) == 1


# =========================================================
# GET BY ID
#
# Cas nominal.
# =========================================================
@patch(
    "app.repositories.hive_repository.get_by_id",
)
def test_get_hive_by_id(
    mock_get_by_id: Mock,
) -> None:

    mock_get_by_id.return_value = fake_hive()

    result = hive_service.get_hive_by_id(
        db=Mock(),
        hive_id=1,
    )

    assert result["id"] == 1


# =========================================================
# Cas important :
#
# Si le repository ne trouve rien,
# le service doit lever une exception HTTP.
#
# C'est la vraie logique métier
# présente dans ce service.
# =========================================================
@patch(
    "app.repositories.hive_repository.get_by_id",
)
def test_get_hive_by_id_not_found(
    mock_get_by_id: Mock,
) -> None:

    mock_get_by_id.return_value = None

    try:
        hive_service.get_hive_by_id(
            db=Mock(),
            hive_id=999,
        )

        assert False

    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Hive not found"


# =========================================================
# DELETE
#
# Vérifie le message retourné.
# =========================================================
@patch(
    "app.repositories.hive_repository.delete",
)
@patch(
    "app.services.hive_service.get_hive_by_id",
)
def test_delete_hive(
    mock_get_hive: Mock,
    mock_delete: Mock,
) -> None:

    mock_get_hive.return_value = fake_hive()

    result = hive_service.delete_hive(
        db=Mock(),
        hive_id=1,
    )

    assert result == {
        "message": "Hive deleted",
    }

    mock_delete.assert_called_once()


# =========================================================
# UPDATE
#
# On vérifie :
#
# - récupération de la ruche
# - modification du nom
# - appel repository.update
#
# C'est la logique métier principale
# de update_hive().
# =========================================================
@patch(
    "app.repositories.hive_repository.update",
)
@patch(
    "app.services.hive_service.get_hive_by_id",
)
def test_update_hive(
    mock_get_hive: Mock,
    mock_update: Mock,
) -> None:

    hive = Mock()
    hive.name = "Ancien nom"

    mock_get_hive.return_value = hive
    mock_update.return_value = hive

    update = Mock()
    update.name = "Nouveau nom"

    hive_service.update_hive(
        db=Mock(),
        hive_id=1,
        hive_update=update,
    )

    assert hive.name == "Nouveau nom"

    mock_update.assert_called_once()
