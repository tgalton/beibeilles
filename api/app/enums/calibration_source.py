from enum import Enum


class CalibrationSource(
    str,
    Enum,
):
    """
    =========================================================
    Origine d'une calibration.
    =========================================================

    MANUAL
    -------
    Calibration saisie manuellement par un utilisateur.

    Exemple :
    - correction connue
    - recalage après maintenance

    AUTO_DRIFT
    ----------
    Calibration calculée automatiquement
    par l'algorithme de détection de dérive.

    Exemple :
    - détection d'une période stable
    - estimation automatique du zéro

    REFERENCE_WEIGHT
    ----------------
    Calibration calculée à partir
    d'un poids étalon connu.

    Exemple :
    - ajout d'un poids de 1 kg
    - vérification de la précision
    - recalcul du gain
    =========================================================
    """

    MANUAL = "manual"

    AUTO_DRIFT = "auto_drift"

    REFERENCE_WEIGHT = "reference_weight"
