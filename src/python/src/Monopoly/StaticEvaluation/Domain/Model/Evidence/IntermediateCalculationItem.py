from dataclasses import dataclass, field
from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject


@dataclass(frozen=True, slots=True)
class IntermediateCalculationItem:
    id: str
    calculationType: str
    description: str
    status: CalculationStatus
    side: CalculationSide
    subject: CalculationSubject
    inputReferences: tuple[str, ...] = ()
    inputValues: dict[str, Any] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)
    formula: str | None = None
    procedure: str | None = None
    intermediateValues: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    unit: str | None = None
    limitations: tuple[str, ...] = ()
    missingInputs: tuple[str, ...] = ()
    dependentCalculationIds: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
