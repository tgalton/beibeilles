import json
import time

import requests
import serial


SERIAL_PORT = "/dev/ttyUSB0"

BAUDRATE = 115200


# =========================================================
# Endpoint IoT générique
#
# Le Raspberry agit comme une gateway IoT :
# - lit la série USB
# - transmet à l'API REST
# =========================================================
API_URL = "http://79.137.34.118:8000/iot/ingest"


def main():

    print(f"Connexion série : {SERIAL_PORT}")

    ser = serial.Serial(
        SERIAL_PORT,
        BAUDRATE,
        timeout=1,
    )

    while True:

        try:

            # =================================================
            # Lecture d'une ligne JSON envoyée
            # par l'ESP32
            # =================================================
            line = ser.readline().decode(
                "utf-8"
            ).strip()

            if not line:
                continue

            print(f"Reçu : {line}")

            payload = json.loads(line)

            # =================================================
            # Transmission HTTP vers FastAPI
            # =================================================
            response = requests.post(
                API_URL,
                json=payload,
                timeout=5,
            )

            print(
                f"Envoyé API : "
                f"{response.status_code}"
            )

            print(response.text)

        except json.JSONDecodeError:
            print("JSON invalide")

        except requests.RequestException as e:
            print(f"Erreur API : {e}")

        except Exception as e:
            print(f"Erreur : {e}")

            time.sleep(2)


if __name__ == "__main__":
    main()