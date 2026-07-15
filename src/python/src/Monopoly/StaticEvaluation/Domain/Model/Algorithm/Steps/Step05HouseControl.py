"""Step 5 — House Supply Control."""

from __future__ import annotations

from Monopoly.StaticEvaluation.Domain.Model.Algorithm.DevelopmentSimulator import DevelopmentSimulator
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.EvidenceCollector import EvidenceCollector
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import SpecificationDefaults


def _houseSide(
    ctx: BoardContext,
    playerId: str,
    side: CalculationSide,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
    sideKey: str,
) -> tuple[int, int]:
    bs = f"board_state_{sideKey}"
    sim = DevelopmentSimulator(ctx, defaults)
    result = sim.simulateAllMonopolies(playerId)

    collector.add(
        f"house_control_{sideKey}_{playerId}",
        "house_control_bonus",
        f"House control bonus for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=result.houseControlBonus,
        inputReferences=(f"{bs}.game_state.available_houses",),
        inputValues={"available_houses": ctx.availableHousesInBank()},
        procedure="Highest configured threshold satisfied by Total Houses Controlled",
        intermediateValues={
            "total_houses_controlled": result.totalHousesControlled,
            "houses_purchased": result.housesPurchased,
        },
        unit="currency",
    )
    collector.add(
        f"house_denial_{sideKey}_{playerId}",
        "house_denial_bonus",
        f"House denial bonus for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=result.houseDenialBonus,
        inputReferences=(f"{bs}.game_state.available_houses",),
        inputValues={"available_houses": ctx.availableHousesInBank()},
        procedure="Highest configured threshold satisfied by Remaining Houses In Bank",
        intermediateValues={"remaining_houses_in_bank": result.remainingHousesInBank},
        unit="currency",
    )
    return result.houseControlBonus, result.houseDenialBonus


def houseControlDelta(
    beforeCtx: BoardContext,
    afterCtx: BoardContext,
    playerId: str,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
) -> tuple[int, int]:
    bcBefore, bdBefore = _houseSide(beforeCtx, playerId, CalculationSide.BEFORE, collector, defaults, "before")
    bcAfter, bdAfter = _houseSide(afterCtx, playerId, CalculationSide.AFTER, collector, defaults, "after")
    controlDelta = bcAfter - bcBefore
    denialDelta = bdAfter - bdBefore
    collector.add(
        f"house_control_delta_{playerId}",
        "house_control_bonus",
        f"House control contribution for {playerId}",
        CalculationStatus.COMPLETE,
        CalculationSide.DELTA,
        CalculationSubject(playerIds=(playerId,)),
        result=controlDelta,
        formula="after - before",
        intermediateValues={"before": bcBefore, "after": bcAfter},
        unit="currency",
    )
    collector.add(
        f"house_denial_delta_{playerId}",
        "house_denial_bonus",
        f"House denial contribution for {playerId}",
        CalculationStatus.COMPLETE,
        CalculationSide.DELTA,
        CalculationSubject(playerIds=(playerId,)),
        result=denialDelta,
        formula="after - before",
        intermediateValues={"before": bdBefore, "after": bdAfter},
        unit="currency",
    )
    return controlDelta, denialDelta
