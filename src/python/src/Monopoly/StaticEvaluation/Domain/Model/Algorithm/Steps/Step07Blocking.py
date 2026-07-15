"""Step 7 — Blocking Value."""

from __future__ import annotations

from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.Algorithm.DevelopmentSimulator import DevelopmentSimulator
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.EvidenceCollector import EvidenceCollector
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import SpecificationDefaults


def _blockingForProperty(
    ctx: BoardContext,
    playerId: str,
    propId: str,
    groupId: str,
    defaults: SpecificationDefaults,
) -> tuple[int, dict[str, Any]]:
    """Compute blocking value for a single property and return (value, detail)."""
    immediate = ctx.immediatelyBlockedPlayers(propId)
    blocked = ctx.blockedPlayers(propId)
    detail: dict[str, Any] = {
        "blocking_property_id": propId,
        "group_id": groupId,
        "blocked_player_ids": sorted(blocked),
        "immediately_blocked_player_ids": sorted(immediate),
    }

    basicValue = defaults.basicBlockingValue if immediate else 0
    detail["basic_blocking_value"] = basicValue

    dangerousBonus = 0
    dangerousBlockedPlayers: list[str] = []
    for blockedPlayer in blocked:
        overrides: dict[str, str | None] = {propId: blockedPlayer}
        hypCtx = BoardContext.withHypotheticalOwnership(ctx.board, ctx.config, overrides)
        if hypCtx.ownsGroup(blockedPlayer, groupId):
            sim = DevelopmentSimulator(hypCtx, defaults)
            cap = sim.evaluateCapability(blockedPlayer, groupId, "dangerous")
            if cap.result:
                dangerousBonus += defaults.dangerousBlockingBonus
                dangerousBlockedPlayers.append(blockedPlayer)
    detail["dangerous_blocked_player_ids"] = sorted(dangerousBlockedPlayers)
    detail["dangerous_monopoly_block_bonus"] = dangerousBonus

    extra = max(0, len(blocked) - 1)
    multiBonus = extra * defaults.multiPlayerBlockingBonus if extra else 0
    detail["additional_blocked_player_count"] = extra
    detail["multi_player_blocking_bonus"] = multiBonus

    needing = ctx.playersNeedingProperty(propId)
    fnBonus = 0
    if needing:
        additional = max(0, len(needing) - 1)
        fnBonus = min(
            defaults.futureNegotiationCap,
            defaults.futureNegotiationBase + additional * defaults.futureNegotiationPerPlayer,
        )
    detail["future_negotiation_bonus"] = fnBonus

    totalValue = basicValue + dangerousBonus + multiBonus + fnBonus
    detail["total_blocking_value"] = totalValue
    return totalValue, detail


def blockingValueSide(
    ctx: BoardContext,
    playerId: str,
    side: CalculationSide,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
    sideKey: str,
) -> int:
    bs = f"board_state_{sideKey}"
    total = 0
    propDetails: list[dict[str, Any]] = []
    propIds: list[str] = []

    for prop in ctx.playerProperties(playerId):
        if prop.category != "street":
            continue
        propIds.append(prop.id)
        value, detail = _blockingForProperty(ctx, playerId, prop.id, prop.groupId, defaults)
        total += value
        propDetails.append(detail)

    collector.add(
        f"blocking_{sideKey}_{playerId}",
        "blocking_value",
        f"Blocking value for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,), propertyIds=tuple(propIds)),
        result=total,
        inputReferences=tuple(f"{bs}.properties[{pid}].owner_player_id" for pid in propIds),
        inputValues={"blocking_property_count": len(propIds)},
        intermediateValues={"per_property": propDetails},
        procedure="Sum basic, dangerous, multi-player, and future negotiation blocking values per blocking property",
        unit="currency",
    )
    return total


def blockingValueDelta(
    beforeCtx: BoardContext,
    afterCtx: BoardContext,
    playerId: str,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
) -> int:
    before = blockingValueSide(beforeCtx, playerId, CalculationSide.BEFORE, collector, defaults, "before")
    after = blockingValueSide(afterCtx, playerId, CalculationSide.AFTER, collector, defaults, "after")
    delta = after - before
    collector.add(
        f"blocking_delta_{playerId}",
        "blocking_value",
        f"Blocking value delta for {playerId}",
        CalculationStatus.COMPLETE,
        CalculationSide.DELTA,
        CalculationSubject(playerIds=(playerId,)),
        result=delta,
        formula="after - before",
        intermediateValues={"before": before, "after": after},
        unit="currency",
    )
    return delta
