from dataclasses import dataclass

from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import EvaluationInput


@dataclass(frozen=True, slots=True)
class EvaluateTradeQuery:
    evaluationInput: EvaluationInput
