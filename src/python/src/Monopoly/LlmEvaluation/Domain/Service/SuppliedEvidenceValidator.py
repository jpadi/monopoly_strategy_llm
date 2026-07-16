"""Classify supplied Static Algorithm Evidence usability."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Domain.Model.Input.JudgeInput import JudgeInput
from Monopoly.LlmEvaluation.Domain.Model.JudgeEnums import EvidenceUsability
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import EvidenceUsabilityResult
from Monopoly.LlmEvaluation.Domain.Service.GeneratedStaticAlgorithmEvidenceValidator import (
    GeneratedStaticAlgorithmEvidenceValidator,
)
from Monopoly.LlmEvaluation.Domain.Service.StaticAlgorithmEvidenceSchema import (
    REGISTERED_CALCULATION_TYPES,
)

MATERIAL_CALCULATION_TYPES_FOR_USABLE = frozenset(
    {
        "strategic_value",
        "trade_ratio",
        "final_static_classification",
    }
)


class SuppliedEvidenceValidator:
    def __init__(
        self,
        *,
        schemaValidator: GeneratedStaticAlgorithmEvidenceValidator | None = None,
    ) -> None:
        self._schemaValidator = schemaValidator or GeneratedStaticAlgorithmEvidenceValidator()

    def classifyAll(
        self,
        judgeInput: JudgeInput,
        requiredAlgorithmId: str,
        requiredAlgorithmVersion: str,
    ) -> tuple[EvidenceUsabilityResult, ...]:
        results: list[EvidenceUsabilityResult] = []
        for evidence in judgeInput.staticAlgorithmEvidence:
            evidenceId = str(evidence.get("id", "unknown"))
            usability = self._classifyOne(
                evidence,
                judgeInput,
                requiredAlgorithmId,
                requiredAlgorithmVersion,
            )
            results.append(EvidenceUsabilityResult(evidenceId=evidenceId, usability=usability))
        return tuple(results)

    def _classifyOne(
        self,
        evidence: dict[str, Any],
        judgeInput: JudgeInput,
        requiredAlgorithmId: str,
        requiredAlgorithmVersion: str,
    ) -> str:
        path = f"static_algorithm_evidence[{evidence.get('id', 'unknown')}]"
        schemaErrors = self._schemaValidator.validate(evidence, path=path)
        if schemaErrors:
            return EvidenceUsability.UNUSABLE

        algoId = evidence.get("algorithm_id")
        algoVersion = evidence.get("algorithm_version")
        if algoId != requiredAlgorithmId or algoVersion != requiredAlgorithmVersion:
            return EvidenceUsability.UNUSABLE

        if not self._identifiersConsistent(evidence, judgeInput):
            return EvidenceUsability.UNUSABLE

        calculations = evidence.get("intermediate_calculations", [])
        if not isinstance(calculations, list) or not calculations:
            return EvidenceUsability.UNUSABLE

        statuses = [str(c.get("status", "UNAVAILABLE")) for c in calculations if isinstance(c, dict)]
        if not statuses or all(s in ("UNAVAILABLE", "ERROR") for s in statuses):
            return EvidenceUsability.UNUSABLE

        if any(s in ("PARTIAL", "UNAVAILABLE", "ERROR") for s in statuses):
            return EvidenceUsability.PARTIALLY_USABLE

        if not self._hasMaterialCalculations(evidence):
            return EvidenceUsability.PARTIALLY_USABLE

        completenessErrors = self._schemaValidator.validateForCompleteExecution(evidence, path=path)
        if completenessErrors:
            return EvidenceUsability.PARTIALLY_USABLE

        unknownTypes = {
            c.get("calculation_type")
            for c in calculations
            if isinstance(c, dict) and c.get("calculation_type") not in REGISTERED_CALCULATION_TYPES
        }
        if unknownTypes:
            return EvidenceUsability.UNUSABLE

        return EvidenceUsability.USABLE

    def _hasMaterialCalculations(self, evidence: dict[str, Any]) -> bool:
        presentTypes = {
            c.get("calculation_type")
            for c in evidence.get("intermediate_calculations", [])
            if isinstance(c, dict) and c.get("status") == "COMPLETE"
        }
        return MATERIAL_CALCULATION_TYPES_FOR_USABLE.issubset(presentTypes)

    def _identifiersConsistent(self, evidence: dict[str, Any], judgeInput: JudgeInput) -> bool:
        knownPlayers = judgeInput.collectReferencedPlayerIds()
        tradeId = judgeInput.trade.get("id")
        for calc in evidence.get("intermediate_calculations", []):
            if not isinstance(calc, dict):
                return False
            subject = calc.get("subject", {})
            if not isinstance(subject, dict):
                return False
            for playerId in subject.get("player_ids", []):
                if str(playerId) not in knownPlayers:
                    return False
            calcTradeId = subject.get("trade_id")
            if calcTradeId is not None and tradeId is not None and str(calcTradeId) != str(tradeId):
                return False
        return True

    @staticmethod
    def bestUsability(results: tuple[EvidenceUsabilityResult, ...]) -> str | None:
        order: dict[str, int] = {
            EvidenceUsability.USABLE: 3,
            EvidenceUsability.PARTIALLY_USABLE: 2,
            EvidenceUsability.UNUSABLE: 1,
        }
        if not results:
            return None
        return max((r.usability for r in results), key=lambda usability: order.get(usability, 0))
