"""Evaluator abstraction for the Static Trade Imbalance Evaluator."""

from __future__ import annotations

from typing import Protocol

from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import EvaluationInput
from Monopoly.StaticEvaluation.Domain.Model.Evidence.StaticAlgorithmEvidence import (
    StaticAlgorithmEvidence,
)


class TradeEvaluator(Protocol):
    """Domain abstraction for trade evaluation.

    Multiple evaluator implementations may exist in the future.
    The application layer depends on this abstraction rather than
    any concrete implementation.
    """

    def evaluate(self, evaluationInput: EvaluationInput) -> StaticAlgorithmEvidence: ...
