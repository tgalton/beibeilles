"""
=========================================================
Installation d'une gateway Beibeilles.
=========================================================

Ce script est exécuté UNE SEULE FOIS
sur le Raspberry.

Son rôle est de stocker :

- gateway_uid
- hmac_secret

dans un fichier local.

Ces informations sont obtenues lors du
provisionnement de la gateway via l'API.

=========================================================
"""

from pathlib import Path

import json


CONFIG_DIR = Path("config")

CONFIG_FILE = CONFIG_DIR / "gateway.json"


def main() -> None:
    """
    Installation locale de la gateway.
    """

    gateway_uid = input(
        "Gateway UID : "
    ).strip()

    hmac_secret = input(
        "HMAC Secret : "
    ).strip()

    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "gateway_uid": gateway_uid,
                "hmac_secret": hmac_secret,
            },
            file,
            indent=4,
        )

    print(
        f"Configuration enregistrée : "
        f"{CONFIG_FILE}"
    )


if __name__ == "__main__":
    main()