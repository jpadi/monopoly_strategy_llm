"""Serialize Judge output to JSON."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Application.Service.EvaluateTradeWithJudgeService import JudgeEvaluationResult
from Monopoly.LlmEvaluation.Domain.Model.Output.JudgeOutput import JudgeOutput


class JudgeOutputSerializer:
    @classmethod
    def toDict(cls, output: JudgeOutput) -> dict[str, Any]:
        return output.toDict()

    @classmethod
    def resultToDict(cls, result: JudgeEvaluationResult) -> dict[str, Any]:
        return {
            "output": cls.toDict(result.output),
            "metadata": {
                "repair_attempted": result.metadata.repairAttempted,
                "repair_count": result.metadata.repairCount,
                "original_validation_errors": list(result.metadata.originalValidationErrors),
            },
        }
