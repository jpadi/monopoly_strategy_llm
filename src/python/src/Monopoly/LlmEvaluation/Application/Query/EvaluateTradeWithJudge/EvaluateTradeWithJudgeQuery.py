"""CQRS query for Judge evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from Monopoly.LlmEvaluation.Domain.Model.Request.JudgeEvaluationRequest import JudgeEvaluationRequest


@dataclass(frozen=True, slots=True)
class EvaluateTradeWithJudgeQuery:
    request: JudgeEvaluationRequest
