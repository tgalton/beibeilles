"""
Fonctions utilitaires HMAC.
"""

from pathlib import Path

import hashlib
import hmac
import json


CONFIG_FILE = (
    Path("config")
    / "gateway.json"
)


def load_gateway_config() -> dict:
    """
    Charge la configuration locale.
    """

    with open(
        CONFIG_FILE,
        encoding="utf-8",
    ) as file:

        return json.load(file)


def build_signature(
    payload: str,
    secret: str,
) -> str:
    """
    Calcule une signature HMAC SHA256.
    """

    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()