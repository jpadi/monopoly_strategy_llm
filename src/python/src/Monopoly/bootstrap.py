"""Manual dependency injection wiring for the Static Evaluator."""

from Monopoly.Shared.Domain.Bus.QueryBus import QueryBus
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQuery import (
    EvaluateTradeQuery,
)
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeQueryHandler import (
    EvaluateTradeQueryHandler,
)
from Monopoly.StaticEvaluation.Application.Query.EvaluateTrade.EvaluateTradeService import (
    EvaluateTradeService,
)
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.StaticTradeEvaluator import (
    StaticTradeEvaluator,
)


def createEvaluateTradeHandler() -> EvaluateTradeQueryHandler:
    evaluator = StaticTradeEvaluator()
    service = EvaluateTradeService(evaluator=evaluator)
    return EvaluateTradeQueryHandler(evaluateTradeService=service)


def createQueryBus() -> QueryBus:
    bus = QueryBus()
    bus.subscribe(EvaluateTradeQuery, createEvaluateTradeHandler().handle)
    return bus
