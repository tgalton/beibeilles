from hashlib import sha256
import hmac
from time import time


MAX_DRIFT_SECONDS = 300


def build_signature_message(
    timestamp: str,
    body: bytes,
) -> bytes:
    """
    =========================================================
    Construit le message signé.

    Format :

        timestamp + body

    Exemple :

        1750871000{"device_serial":"ESP32"}
    =========================================================
    """

    return timestamp.encode() + body


def compute_hmac_signature(
    secret: str,
    timestamp: str,
    body: bytes,
) -> str:
    """
    =========================================================
    Calcule la signature HMAC SHA256.
    =========================================================
    """

    message = build_signature_message(
        timestamp=timestamp,
        body=body,
    )

    return hmac.new(
        secret.encode(),
        message,
        sha256,
    ).hexdigest()


def validate_timestamp(
    timestamp: str,
) -> bool:
    """
    =========================================================
    Vérifie que la requête n'est pas trop ancienne.

    Fenêtre :
        +/- 5 minutes
    =========================================================
    """

    try:
        request_ts = int(timestamp)

    except ValueError:
        return False

    current_ts = int(time())

    return (
        abs(
            current_ts - request_ts
        )
        <= MAX_DRIFT_SECONDS
    )


def verify_signature(
    secret: str,
    timestamp: str,
    body: bytes,
    received_signature: str,
) -> bool:
    """
    =========================================================
    Compare la signature calculée
    avec celle reçue.
    =========================================================
    """

    expected_signature = (
        compute_hmac_signature(
            secret=secret,
            timestamp=timestamp,
            body=body,
        )
    )

    return hmac.compare_digest(
        expected_signature,
        received_signature,
    )