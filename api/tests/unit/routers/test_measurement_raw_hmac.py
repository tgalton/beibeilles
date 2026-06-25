# TODO: Ajouter les tests d'intégration
# import json
# import time
# import hmac
# import hashlib

# from fastapi.testclient import TestClient

# from app.main import app
# from app.models.gateway import Gateway
# from app.database import get_db

# # Ici on bypass uniquement la validation externe inutile (DB réelle ok, ou factory test).
# def sign_request(secret: str, timestamp: str, body: dict) -> str:

#     body_bytes = json.dumps(
#         body,
#         separators=(",", ":"),
#     ).encode()

#     message = timestamp.encode() + body_bytes

#     return hmac.new(
#         secret.encode(),
#         message,
#         hashlib.sha256,
#     ).hexdigest()

# client = TestClient(app)


# def test_ingest_measurements_hmac_integration(db_session):
#     """
#     Test E2E :
#     FastAPI + HMAC + Gateway réelle logique.
#     """

#     # =====================================================
#     # 1. Création gateway en base
#     # =====================================================
#     gateway = Gateway(
#         name="test-gateway",
#         gateway_uid="gw_test_123",
#         hmac_secret="super-secret",
#         is_active=True,
#     )

#     db_session.add(gateway)
#     db_session.commit()
#     db_session.refresh(gateway)

#     # =====================================================
#     # 2. Payload IoT réel
#     # =====================================================
#     payload = {
#         "device_serial": "ESP32-001",
#         "measurements": [
#             {
#                 "type": "weight",
#                 "value": 12.3,
#                 "hive_level_id": 1,
#             }
#         ],
#     }

#     # =====================================================
#     # 3. Timestamp + signature (comme Raspberry)
#     # =====================================================
#     timestamp = str(int(time.time()))

#     signature = sign_request(
#         secret=gateway.hmac_secret,
#         timestamp=timestamp,
#         body=payload,
#     )

#     # =====================================================
#     # 4. Request HTTP réelle
#     # =====================================================
#     response = client.post(
#         "/measurements/raw/ingest",
#         json=payload,
#         headers={
#             "X-Gateway-Uid": gateway.gateway_uid,
#             "X-Timestamp": timestamp,
#             "X-Signature": signature,
#         },
#     )

#     # =====================================================
#     # 5. Assertions
#     # =====================================================
#     assert response.status_code == 200

#     assert isinstance(response.json(), list)


# def test_ingest_measurements_hmac_invalid_signature(db_session):

#     gateway = Gateway(
#         name="test-gateway",
#         gateway_uid="gw_test_123",
#         hmac_secret="super-secret",
#         is_active=True,
#     )

#     db_session.add(gateway)
#     db_session.commit()

#     payload = {
#         "device_serial": "ESP32-001",
#         "measurements": [],
#     }

#     timestamp = str(int(time.time()))

#     response = client.post(
#         "/measurements/raw/ingest",
#         json=payload,
#         headers={
#             "X-Gateway-Uid": gateway.gateway_uid,
#             "X-Timestamp": timestamp,
#             "X-Signature": "invalid-signature",
#         },
#     )

#     assert response.status_code == 401
