from secrets import token_hex


def generate_gateway_uid() -> str:
    """
    =========================================================
    Génère un identifiant public de gateway.
    =========================================================

    Cet identifiant est utilisé par le Raspberry
    dans les headers HTTP pour s'identifier.

    Exemple :

        gw_a1b2c3d4e5f6g7h8

    Ce n'est PAS un secret.

    Returns
    -------
    str
        Identifiant unique de gateway.
    =========================================================
    """

    return f"gw_{token_hex(8)}"


def generate_hmac_secret() -> str:
    """
    =========================================================
    Génère un secret HMAC aléatoire.

    Ce secret est partagé uniquement entre :
    - le Raspberry
    - le backend FastAPI

    Il sert à signer les requêtes HTTP.

    Exemple :

        4d8b1f0a7e6c...

    Returns
    -------
    str
        Secret HMAC cryptographiquement aléatoire.
    =========================================================
    """

    return token_hex(32)