from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalcIdGenerator import CalcIdGenerator
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.IntermediateCalculationItem import (
    IntermediateCalculationItem,
)


@dataclass
class EvidenceCollector:
    """Accumulates intermediate calculation items with deterministic IDs."""

    calcIds: CalcIdGenerator = field(default_factory=CalcIdGenerator)
    items: list[IntermediateCalculationItem] = field(default_factory=list)
    idByKey: dict[str, str] = field(default_factory=dict)

    def add(
        self,
        key: str,
        calculationType: str,
        description: str,
        status: CalculationStatus | str,
        side: CalculationSide | str,
        subject: CalculationSubject,
        result: Any = None,
        *,
        inputReferences: tuple[str, ...] = (),
        inputValues: dict[str, Any] | None = None,
        sources: dict[str, str] | None = None,
        formula: str | None = None,
        procedure: str | None = None,
        intermediateValues: dict[str, Any] | None = None,
        unit: str | None = None,
        limitations: tuple[str, ...] = (),
        missingInputs: tuple[str, ...] = (),
        dependentCalculationIds: tuple[str, ...] = (),
        metadata: dict[str, Any] | None = None,
    ) -> str:
        resolvedStatus = CalculationStatus(status) if isinstance(status, str) else status
        resolvedSide = CalculationSide(side) if isinstance(side, str) else side
        calcId = self.calcIds.next()
        self.idByKey[key] = calcId
        self.items.append(
            IntermediateCalculationItem(
                id=calcId,
                calculationType=calculationType,
                description=description,
                status=resolvedStatus,
                side=resolvedSide,
                subject=subject,
                inputReferences=inputReferences,
                inputValues=inputValues or {},
                sources=sources or {},
                formula=formula,
                procedure=procedure,
                intermediateValues=intermediateValues or {},
                result=result,
                unit=unit,
                limitations=limitations,
                missingInputs=missingInputs,
                dependentCalculationIds=dependentCalculationIds,
                metadata=metadata or {},
            )
        )
        return calcId

    def getId(self, key: str) -> str | None:
        return self.idByKey.get(key)

    def linkDependency(self, upstreamKey: str, downstreamKey: str) -> None:
        """Record that the item at upstreamKey feeds into downstreamKey."""
        upId = self.idByKey.get(upstreamKey)
        downId = self.idByKey.get(downstreamKey)
        if upId is None or downId is None:
            return
        for item in self.items:
            if item.id == upId:
                deps = list(item.dependentCalculationIds)
                if downId not in deps:
                    deps.append(downId)
                    object.__setattr__(item, "dependentCalculationIds", tuple(deps))
                break
