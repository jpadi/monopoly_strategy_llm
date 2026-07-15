"""Test fixtures for EvaluateTradeQuery functional tests.

Functional tests execute through the real Query Bus.
"""

from __future__ import annotations

from typing import Any

import pytest

from Monopoly.bootstrap import createQueryBus
from Monopoly.Shared.Domain.Bus.QueryBus import QueryBus
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQuery import (
    EvaluateTradeQuery,
)
from Monopoly.StaticEvaluation.Infrastructure.Json.EvaluationInputMapper import (
    EvaluationInputMapper,
)
from Monopoly.StaticEvaluation.Infrastructure.Json.EvidenceSerializer import (
    EvidenceSerializer,
)


@pytest.fixture
def query_bus() -> QueryBus:
    """Provide the configured Query Bus."""
    return createQueryBus()


@pytest.fixture
def execute_query(query_bus: QueryBus):
    """Provide a helper function to execute a query through the bus."""

    def _execute(input_data: dict[str, Any]) -> dict[str, Any]:
        evaluation_input = EvaluationInputMapper.fromDict(input_data)
        query = EvaluateTradeQuery(evaluationInput=evaluation_input)
        evidence = query_bus.ask(query)
        return EvidenceSerializer.toDict(evidence)

    return _execute
