from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQuery import (
    EvaluateTradeQuery,
)
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeService import (
    EvaluateTradeService,
)
from Monopoly.StaticEvaluation.Domain.Model.Evidence.StaticAlgorithmEvidence import (
    StaticAlgorithmEvidence,
)


class EvaluateTradeQueryHandler:
    """Thin query handler delegating to EvaluateTradeService."""

    def __init__(self, *, evaluateTradeService: EvaluateTradeService) -> None:
        self._service = evaluateTradeService

    def handle(self, query: EvaluateTradeQuery) -> StaticAlgorithmEvidence:
        return self._service.execute(query)
