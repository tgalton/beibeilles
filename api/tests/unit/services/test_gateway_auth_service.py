from time import time

from app.services import gateway_auth_service

# Test build_signature_message
def test_build_signature_message():

    timestamp = "123456"

    body = b'{"hello":"world"}'

    message = (
        gateway_auth_service.build_signature_message(
            timestamp=timestamp,
            body=body,
        )
    )

    assert (
        message
        == b'123456{"hello":"world"}'
    )

# Test compute_hmac_signature
def test_compute_hmac_signature():

    signature_1 = (
        gateway_auth_service.compute_hmac_signature(
            secret="my-secret",
            timestamp="123456",
            body=b"hello",
        )
    )

    signature_2 = (
        gateway_auth_service.compute_hmac_signature(
            secret="my-secret",
            timestamp="123456",
            body=b"hello",
        )
    )

    assert signature_1 == signature_2


# Test changement du body
def test_compute_hmac_signature_changes_if_body_changes():

    signature_1 = (
        gateway_auth_service.compute_hmac_signature(
            secret="my-secret",
            timestamp="123456",
            body=b"hello",
        )
    )

    signature_2 = (
        gateway_auth_service.compute_hmac_signature(
            secret="my-secret",
            timestamp="123456",
            body=b"world",
        )
    )

    assert signature_1 != signature_2

# Timestamp valide
def test_validate_timestamp_valid():

    timestamp = str(
        int(time())
    )

    assert (
        gateway_auth_service.validate_timestamp(
            timestamp,
        )
        is True
    )

# Timestamp trop vieux
def test_validate_timestamp_too_old():

    timestamp = str(
        int(time()) - 1000
    )

    assert (
        gateway_auth_service.validate_timestamp(
            timestamp,
        )
        is False
    )

# Timestamp invalide
def test_validate_timestamp_invalid():

    assert (
        gateway_auth_service.validate_timestamp(
            "bonjour",
        )
        is False
    )

# Signature valide
def test_verify_signature_valid():

    secret = "super-secret"

    timestamp = "123456"

    body = b'{"value":42}'

    signature = (
        gateway_auth_service.compute_hmac_signature(
            secret=secret,
            timestamp=timestamp,
            body=body,
        )
    )

    assert (
        gateway_auth_service.verify_signature(
            secret=secret,
            timestamp=timestamp,
            body=body,
            received_signature=signature,
        )
        is True
    )

# Signature invalide
def test_verify_signature_invalid():

    assert (
        gateway_auth_service.verify_signature(
            secret="secret",
            timestamp="123456",
            body=b"hello",
            received_signature="fake",
        )
        is False
    )