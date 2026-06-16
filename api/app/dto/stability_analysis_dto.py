from dataclasses import dataclass


@dataclass(slots=True)
class StabilityAnalysisDTO:
    """
    Résultat complet d'analyse
    d'une fenêtre de stabilité.
    """

    standard_deviation_kg: float

    slope_kg_per_hour: float

    duration_minutes: int

    confidence: float

    is_stable: bool