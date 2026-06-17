from dataclasses import dataclass


@dataclass(slots=True)
class BaselineCandidateDTO:
    hive_level_id: int

    baseline_offset_kg: float

    confidence: float

    stable_duration_minutes: int

    algorithm_version: str
