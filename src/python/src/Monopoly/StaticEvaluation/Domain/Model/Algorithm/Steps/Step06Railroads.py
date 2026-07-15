"""Step 6 — Railroad Evaluation."""

from __future__ import annotations

from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.EvidenceCollector import EvidenceCollector
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import (
    RAILROAD_GROUP,
    SpecificationDefaults,
)


def _railroadSide(
    ctx: BoardContext,
    playerId: str,
    side: CalculationSide,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
    sideKey: str,
) -> int:
    count = ctx.railroadCount(playerId)
    base = defaults.railroadValues.get(count, 0)
    devCount = ctx.developedMonopolyCount()
    developedGroupIds = ctx.developedMonopolyGroupIds()
    lowDevelopment = devCount <= 1
    if lowDevelopment:
        mult = defaults.railroadLowDevelopmentMultiplier
        contextLabel = "low_development"
        threshold = "<= 1"
    else:
        mult = defaults.railroadHighDevelopmentMultiplier
        contextLabel = "high_development"
        threshold = ">= 2"
    value = int(base * mult)
    bs = f"board_state_{sideKey}"
    railroadIds = tuple(p.id for p in ctx.playerProperties(playerId) if p.groupId == RAILROAD_GROUP)
    inputRefs: list[str] = [f"{bs}.properties[{rid}].owner_player_id" for rid in railroadIds]
    for groupId in developedGroupIds:
        for prop in ctx.groupProperties(groupId):
            if prop.houses >= 1 or prop.hasHotel:
                inputRefs.append(f"{bs}.properties[{prop.id}].houses")
                inputRefs.append(f"{bs}.properties[{prop.id}].has_hotel")
    collector.add(
        f"railroad_{sideKey}_{playerId}",
        "railroad_value",
        f"Railroad value for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(
            playerIds=(playerId,),
            propertyIds=railroadIds,
            groupIds=tuple(developedGroupIds),
        ),
        result=value,
        inputReferences=tuple(inputRefs),
        inputValues={"railroad_count": count},
        formula="Railroad Base Value x Board Context Multiplier",
        intermediateValues={
            "railroad_count": count,
            "base_value": base,
            "context_predicate_name": "developed_monopoly_count",
            "developed_monopoly_count": devCount,
            "developed_monopoly_group_ids": developedGroupIds,
            "context_predicate_threshold": threshold,
            "context_predicate_result": lowDevelopment,
            "context_multiplier": mult,
            "context_label": contextLabel,
        },
        sources={"base_value": "SPECIFICATION_DEFAULT", "context_multiplier": "SPECIFICATION_DEFAULT"},
        procedure=(
            "Apply low_development multiplier (1.30) when developed_monopoly_count <= 1;"
            " otherwise apply high_development multiplier (0.80)"
        ),
        unit="currency",
    )
    return value


def railroadValueDelta(
    beforeCtx: BoardContext,
    afterCtx: BoardContext,
    playerId: str,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
) -> int:
    before = _railroadSide(beforeCtx, playerId, CalculationSide.BEFORE, collector, defaults, "before")
    after = _railroadSide(afterCtx, playerId, CalculationSide.AFTER, collector, defaults, "after")
    delta = after - before
    collector.add(
        f"railroad_delta_{playerId}",
        "railroad_value",
        f"Railroad value delta for {playerId}",
        CalculationStatus.COMPLETE,
        CalculationSide.DELTA,
        CalculationSubject(playerIds=(playerId,)),
        result=delta,
        formula="after - before",
        intermediateValues={"before": before, "after": after},
        unit="currency",
    )
    return delta
