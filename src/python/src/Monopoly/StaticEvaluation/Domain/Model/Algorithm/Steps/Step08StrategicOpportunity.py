"""Step 8 — Strategic Opportunity Evaluation."""

from __future__ import annotations

from Monopoly.StaticEvaluation.Domain.Model.Algorithm.Predicates import (
    isDangerousMonopolyAvailable,
    isFullyBlockedBoard,
)
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.EvidenceCollector import EvidenceCollector
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import SpecificationDefaults


def _scoreSide(
    ctx: BoardContext,
    playerId: str,
    side: CalculationSide,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
    sideKey: str,
) -> int:
    criteria: dict[str, bool] = {}

    # Negotiation leverage
    leverage = False
    for prop in ctx.playerProperties(playerId):
        if ctx.playersNeedingProperty(prop.id):
            leverage = True
            break
    criteria["negotiation_leverage"] = leverage

    # Board control — blocking in 2+ groups
    blockingGroups = set()
    for prop in ctx.playerProperties(playerId):
        if prop.category == "street" and ctx.blockedPlayers(prop.id):
            blockingGroups.add(prop.groupId)
    criteria["board_control"] = len(blockingGroups) >= 2

    # Multiple monopoly potential
    criteria["multiple_monopoly_potential"] = len(ctx.oneFromMonopoly(playerId)) >= 2

    # Fully blocked board
    criteria["fully_blocked_board"] = isFullyBlockedBoard(ctx, playerId)
    dangerousKeys: list[str] = []
    bs = f"board_state_{sideKey}"
    for opponentId in ctx.opponentIds(playerId):
        for gid in ctx.streetGroups():
            avail, evidence = isDangerousMonopolyAvailable(ctx, opponentId, gid, boardStateKey=bs)
            dangerousKey = f"dangerous_avail_{sideKey}_{playerId}_{opponentId}_{gid}"
            dangerousKeys.append(dangerousKey)
            collector.add(
                dangerousKey,
                "dangerous_monopoly_availability",
                f"Dangerous monopoly availability for {opponentId} group {gid}",
                CalculationStatus.COMPLETE,
                side,
                CalculationSubject(playerIds=(opponentId,), groupIds=(gid,)),
                result=avail,
                inputReferences=evidence.inputReferences,
                inputValues=evidence.inputValues,
                intermediateValues=evidence.intermediateValues,
                procedure=(
                    "Hypothetical zero-cost assignment of unowned group properties,"
                    " then Dangerous predicate evaluation with candidate-group"
                    " mortgage capacity excluded from construction budget"
                ),
                unit="boolean",
            )

    satisfied = sum(1 for v in criteria.values() if v)
    score = min(
        defaults.strategicOpportunityCap,
        satisfied * defaults.strategicOpportunityPerCriterion,
    )

    bs = f"board_state_{sideKey}"
    oppKey = f"strategic_opp_{sideKey}_{playerId}"
    collector.add(
        oppKey,
        "strategic_opportunity_score",
        f"Strategic opportunity score for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=score,
        inputReferences=(f"{bs}.players[{playerId}].owned_properties",),
        inputValues={"criteria_evaluated": list(criteria.keys())},
        intermediateValues={"criteria": criteria, "satisfied_count": satisfied},
        formula="200 × criteria satisfied, capped at 800",
        unit="currency",
    )
    for dangerousKey in dangerousKeys:
        collector.linkDependency(dangerousKey, oppKey)
    return score


def strategicOpportunityDelta(
    beforeCtx: BoardContext,
    afterCtx: BoardContext,
    playerId: str,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
) -> int:
    before = _scoreSide(beforeCtx, playerId, CalculationSide.BEFORE, collector, defaults, "before")
    after = _scoreSide(afterCtx, playerId, CalculationSide.AFTER, collector, defaults, "after")
    delta = after - before
    collector.add(
        f"strategic_opp_delta_{playerId}",
        "strategic_opportunity_score",
        f"Strategic opportunity delta for {playerId}",
        CalculationStatus.COMPLETE,
        CalculationSide.DELTA,
        CalculationSubject(playerIds=(playerId,)),
        result=delta,
        formula="after - before",
        intermediateValues={"before": before, "after": after},
        unit="currency",
    )
    collector.linkDependency(f"strategic_opp_before_{playerId}", f"strategic_opp_delta_{playerId}")
    collector.linkDependency(f"strategic_opp_after_{playerId}", f"strategic_opp_delta_{playerId}")
    return delta
