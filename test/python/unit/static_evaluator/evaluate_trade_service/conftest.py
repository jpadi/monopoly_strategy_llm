"""Test fixtures for EvaluateTradeService unit tests.

This conftest provides the application service fixture for all unit tests.
The service is injected through the test fixture - tests do not construct
the service, evaluator, or any dependencies directly.
"""

from __future__ import annotations

from typing import Any

import pytest

from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQuery import (
    EvaluateTradeQuery,
)
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeService import (
    EvaluateTradeService,
)
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.StaticTradeEvaluator import (
    StaticTradeEvaluator,
)
from Monopoly.StaticEvaluation.Infrastructure.Json.EvaluationInputMapper import (
    EvaluationInputMapper,
)
from Monopoly.StaticEvaluation.Infrastructure.Json.EvidenceSerializer import (
    EvidenceSerializer,
)


@pytest.fixture
def evaluate_trade_service() -> EvaluateTradeService:
    """Provide the configured EvaluateTradeService."""
    evaluator = StaticTradeEvaluator()
    return EvaluateTradeService(evaluator=evaluator)


@pytest.fixture
def execute_scenario(evaluate_trade_service: EvaluateTradeService):
    """Provide a helper function to execute a scenario and get serialized evidence."""

    def _execute(input_data: dict[str, Any]) -> dict[str, Any]:
        evaluation_input = EvaluationInputMapper.fromDict(input_data)
        query = EvaluateTradeQuery(evaluationInput=evaluation_input)
        evidence = evaluate_trade_service.execute(query)
        return EvidenceSerializer.toDict(evidence)

    return _execute


@pytest.fixture
def player_a_id() -> str:
    """Standard Player A ID used in fixtures."""
    return "player_a"


@pytest.fixture
def player_b_id() -> str:
    """Standard Player B ID used in fixtures."""
    return "player_b"
