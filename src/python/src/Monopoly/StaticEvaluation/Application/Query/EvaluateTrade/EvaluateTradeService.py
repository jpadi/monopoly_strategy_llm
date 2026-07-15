from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQuery import (
    EvaluateTradeQuery,
)
from Monopoly.StaticEvaluation.Domain.Model.EvaluationInputValidator import (
    validateEvaluationInput,
)
from Monopoly.StaticEvaluation.Domain.Model.Evidence.StaticAlgorithmEvidence import (
    StaticAlgorithmEvidence,
)
from Monopoly.StaticEvaluation.Domain.Model.TradeEvaluator import TradeEvaluator


class EvaluateTradeService:
    """Side-effect-free read service for trade evaluation."""

    def __init__(self, *, evaluator: TradeEvaluator) -> None:
        self._evaluator = evaluator

    def execute(self, query: EvaluateTradeQuery) -> StaticAlgorithmEvidence:
        validateEvaluationInput(query.evaluationInput)
        return self._evaluator.evaluate(query.evaluationInput)
