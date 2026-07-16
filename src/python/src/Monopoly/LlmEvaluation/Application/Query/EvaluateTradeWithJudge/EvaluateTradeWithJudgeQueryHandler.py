"""Query handler for Judge evaluation."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Application.Query.EvaluateTradeWithJudge.EvaluateTradeWithJudgeQuery import (
    EvaluateTradeWithJudgeQuery,
)
from Monopoly.LlmEvaluation.Application.Service.EvaluateTradeWithJudgeService import (
    EvaluateTradeWithJudgeService,
    JudgeEvaluationResult,
)


class EvaluateTradeWithJudgeQueryHandler:
    def __init__(self, *, evaluateTradeWithJudgeService: EvaluateTradeWithJudgeService) -> None:
        self._service = evaluateTradeWithJudgeService

    def handle(self, query: EvaluateTradeWithJudgeQuery) -> JudgeEvaluationResult:
        return self._service.execute(query.request)
