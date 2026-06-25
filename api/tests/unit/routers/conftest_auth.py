from app.models.gateway import Gateway


# =========================================================
# Fake gateway (bypass HMAC)
# =========================================================
def override_auth_gateway():
    """
    Gateway fake injectée dans les tests.
    """

    return Gateway(
        id=1,
        name="test-gateway",
        gateway_uid="test-gw",
        hmac_secret="test-secret",
        is_active=True,
    )