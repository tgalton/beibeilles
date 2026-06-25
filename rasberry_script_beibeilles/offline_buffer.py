"""
=========================================================
Buffer hors ligne des mesures.
=========================================================

Objectif :

Si l'API est indisponible :

- coupure internet
- serveur en maintenance
- erreur réseau

les mesures ne doivent jamais être perdues.

Elles sont stockées dans un fichier local.

Lors du prochain envoi réussi :

- les anciennes mesures sont renvoyées
- le buffer est vidé

=========================================================
"""

from pathlib import Path

import json


BUFFER_FILE = Path(
    "offline_measurements.json"
)


def load_buffer() -> list[dict]:
    """
    Charge les mesures en attente.
    """

    if not BUFFER_FILE.exists():
        return []

    with open(
        BUFFER_FILE,
        encoding="utf-8",
    ) as file:

        return json.load(file)


def save_buffer(
    measurements: list[dict],
) -> None:
    """
    Sauvegarde le buffer.
    """

    with open(
        BUFFER_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            measurements,
            file,
            indent=4,
        )


def add_to_buffer(
    payload: dict,
) -> None:
    """
    Ajoute un payload au buffer.
    """

    measurements = load_buffer()

    measurements.append(payload)

    save_buffer(measurements)


def clear_buffer() -> None:
    """
    Vide le buffer.
    """

    save_buffer([])