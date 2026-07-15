from dataclasses import dataclass, field
from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.Evidence.IntermediateCalculationItem import (
    IntermediateCalculationItem,
)


@dataclass(frozen=True, slots=True)
class StaticAlgorithmEvidence:
    id: str
    algorithmId: str
    algorithmName: str
    algorithmVersion: str
    purpose: str
    intermediateCalculations: tuple[IntermediateCalculationItem, ...] = ()
    finalConclusions: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    statistics: dict[str, Any] = field(default_factory=dict)
