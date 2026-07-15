"""Serialize StaticAlgorithmEvidence to JSON-compatible dict."""

from __future__ import annotations

from enum import Enum
from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.IntermediateCalculationItem import (
    IntermediateCalculationItem,
)
from Monopoly.StaticEvaluation.Domain.Model.Evidence.StaticAlgorithmEvidence import (
    StaticAlgorithmEvidence,
)


class EvidenceSerializer:
    @classmethod
    def toDict(cls, evidence: StaticAlgorithmEvidence) -> dict[str, Any]:
        return {
            "id": evidence.id,
            "algorithm_id": evidence.algorithmId,
            "algorithm_name": evidence.algorithmName,
            "algorithm_version": evidence.algorithmVersion,
            "purpose": evidence.purpose,
            "intermediate_calculations": [cls._itemToDict(item) for item in evidence.intermediateCalculations],
            "final_conclusions": cls._sanitize(evidence.finalConclusions),
            "metadata": cls._sanitize(evidence.metadata),
            "statistics": cls._sanitize(evidence.statistics),
        }

    @classmethod
    def _itemToDict(cls, item: IntermediateCalculationItem) -> dict[str, Any]:
        return {
            "id": item.id,
            "calculation_type": item.calculationType,
            "description": item.description,
            "status": item.status.value if isinstance(item.status, CalculationStatus) else item.status,
            "side": item.side.value if isinstance(item.side, CalculationSide) else item.side,
            "subject": cls._subjectToDict(item.subject),
            "input_references": list(item.inputReferences),
            "input_values": cls._sanitize(item.inputValues),
            "sources": cls._sanitize(item.sources),
            "formula": item.formula,
            "procedure": item.procedure,
            "intermediate_values": cls._sanitize(item.intermediateValues),
            "result": cls._sanitizeValue(item.result),
            "unit": item.unit,
            "limitations": list(item.limitations),
            "missing_inputs": list(item.missingInputs),
            "dependent_calculation_ids": list(item.dependentCalculationIds),
            "metadata": cls._sanitize(item.metadata),
        }

    @classmethod
    def _subjectToDict(cls, subject: CalculationSubject) -> dict[str, Any]:
        return {
            "player_ids": list(subject.playerIds),
            "property_ids": list(subject.propertyIds),
            "group_ids": list(subject.groupIds),
            "trade_id": subject.tradeId,
            "transfer_ids": list(subject.transferIds),
        }

    @classmethod
    def _sanitize(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {cls._sanitizeValue(k): cls._sanitizeValue(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._sanitizeValue(item) for item in value]
        return cls._sanitizeValue(value)

    @classmethod
    def _sanitizeValue(cls, value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return cls._sanitize(value)
        if isinstance(value, (list, tuple)):
            return [cls._sanitizeValue(item) for item in value]
        return value
