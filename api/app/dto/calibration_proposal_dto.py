from dataclasses import dataclass
from app.enums.calibration_source import (
    CalibrationSource,
)

@dataclass(slots=True)
class CalibrationProposalDTO:
    """
    =====================================================
    Proposition de calibration générée
    par l'algorithme.
    =====================================================

    IMPORTANT :

    Cette structure ne représente PAS
    une calibration active.

    Elle représente uniquement une
    suggestion calculée par le système.

    Cette proposition pourra ensuite :

    - être validée automatiquement ;
    - être validée manuellement ;
    - être rejetée.

    =====================================================
    offset_kg
    =====================================================

    Décalage détecté sur la balance.

    Exemple :

        poids réel      = 50.0 kg
        poids observé   = 51.2 kg

        offset = +1.2 kg

    Le poids corrigé deviendra :

        poids_mesuré - offset

    =====================================================
    gain
    =====================================================

    Coefficient multiplicatif appliqué
    aux variations de poids.

    Exemple :

        attendu = 1.000 kg
        mesuré  = 0.950 kg

        gain = 1.0526

    =====================================================
    confidence
    =====================================================

    Niveau de confiance de l'algorithme.

    Valeur comprise entre :

        0.0
        et
        1.0

    =====================================================
    source
    =====================================================

    Origine de la proposition.

    Exemples :

        AUTO_DRIFT
        REFERENCE_WEIGHT

    =====================================================
    algorithm_version
    =====================================================

    Version de l'algorithme ayant produit
    cette proposition.

    Permet d'auditer ultérieurement
    les décisions prises par le système.
    =====================================================
    """

    offset_kg: float

    gain: float

    confidence: float

    source: CalibrationSource

    algorithm_version: str