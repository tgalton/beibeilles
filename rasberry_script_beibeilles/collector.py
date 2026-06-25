"""
=========================================================
Collector Raspberry Beibeilles
=========================================================

Rôle :

- lire les données envoyées par l'ESP32
- signer les requêtes HMAC
- envoyer les mesures à l'API
- conserver les mesures hors ligne
- resynchroniser automatiquement

=========================================================
"""

import json
import time

import requests
import serial

from hmac_utils import (
    build_signature,
    load_gateway_config,
)

from offline_buffer import (
    add_to_buffer,
    clear_buffer,
    load_buffer,
)


# =========================================================
# Configuration série
# =========================================================

SERIAL_PORT = "/dev/ttyUSB0"

BAUDRATE = 115200


# =========================================================
# Endpoint API
# =========================================================

API_URL = (
    "http://79.137.34.118:8000"
    "/measurements/raw/ingest"
)


# =========================================================
# Configuration gateway
# =========================================================

gateway_config = (
    load_gateway_config()
)

GATEWAY_UID = (
    gateway_config["gateway_uid"]
)

HMAC_SECRET = (
    gateway_config["hmac_secret"]
)


def send_payload(
    payload: dict,
) -> bool:
    """
    =====================================================
    Envoie un payload vers l'API.

    Retourne :
        True  -> succès
        False -> échec
    =====================================================
    """

    payload_json = json.dumps(
        payload,
        separators=(",", ":"),
    )

    signature = build_signature(
        payload=payload_json,
        secret=HMAC_SECRET,
    )

    headers = {
        "X-Gateway-Uid": GATEWAY_UID,
        "X-Signature": signature,
        "Content-Type": "application/json",
    }

    try:

        response = requests.post(
            API_URL,
            data=payload_json,
            headers=headers,
            timeout=5,
        )

        response.raise_for_status()

        print(
            f"API OK : {response.status_code}"
        )

        return True

    except requests.RequestException as e:

        print(
            f"Erreur API : {e}"
        )

        return False


def sync_offline_buffer() -> None:
    """
    =====================================================
    Tente de renvoyer toutes les mesures
    stockées localement.
    =====================================================
    """

    buffered_payloads = load_buffer()

    if not buffered_payloads:
        return

    print(
        f"Synchronisation de "
        f"{len(buffered_payloads)} "
        f"payload(s)"
    )

    remaining_payloads = []

    for payload in buffered_payloads:

        success = send_payload(payload)

        if not success:
            remaining_payloads.append(
                payload
            )

    if not remaining_payloads:

        clear_buffer()

        print(
            "Buffer synchronisé."
        )

    else:

        from offline_buffer import (
            save_buffer,
        )

        save_buffer(
            remaining_payloads
        )

        print(
            f"{len(remaining_payloads)} "
            f"payload(s) restant(s)"
        )


def main() -> None:
    """
    Boucle principale.
    """

    print(
        f"Connexion série : "
        f"{SERIAL_PORT}"
    )

    ser = serial.Serial(
        SERIAL_PORT,
        BAUDRATE,
        timeout=1,
    )

    while True:

        try:

            # =============================================
            # Synchronisation du buffer
            # =============================================

            sync_offline_buffer()

            # =============================================
            # Lecture série
            # =============================================

            line = (
                ser.readline()
                .decode("utf-8")
                .strip()
            )

            if not line:
                continue

            print(
                f"Reçu : {line}"
            )

            payload = json.loads(
                line
            )

            # =============================================
            # Envoi API
            # =============================================

            success = send_payload(
                payload
            )

            if not success:

                print(
                    "Ajout au buffer local"
                )

                add_to_buffer(
                    payload
                )

        except json.JSONDecodeError:

            print(
                "JSON invalide"
            )

        except Exception as e:

            print(
                f"Erreur : {e}"
            )

            time.sleep(2)


if __name__ == "__main__":
    main()