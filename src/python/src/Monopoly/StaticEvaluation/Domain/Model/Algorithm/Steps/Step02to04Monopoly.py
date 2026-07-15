"""Steps 2–4: Monopoly detection, development potential, monopoly strength."""

from __future__ import annotations

from Monopoly.StaticEvaluation.Domain.Model.Algorithm.DevelopmentSimulator import DevelopmentSimulator
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.RentResolver import RentResolution, RentResolver
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.EvidenceCollector import EvidenceCollector
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import SpecificationDefaults


def monopolyValueForSide(
    ctx: BoardContext,
    playerId: str,
    side: CalculationSide,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
    sideKey: str,
) -> int:
    sim = DevelopmentSimulator(ctx, defaults)
    resolver = RentResolver(ctx)
    total: int | None = 0

    bs = f"board_state_{sideKey}"
    mc = sim.mortgageCapacity(playerId)
    mortgageableProps = [
        p for p in ctx.playerProperties(playerId) if not p.isMortgaged and p.houses == 0 and not p.hasHotel
    ]
    collector.add(
        f"mortgage_cap_{sideKey}_{playerId}",
        "mortgage_capacity",
        f"Mortgage capacity for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(
            playerIds=(playerId,),
            propertyIds=tuple(p.id for p in mortgageableProps),
        ),
        result=mc,
        inputReferences=tuple(f"{bs}.properties[{p.id}].mortgage_value" for p in mortgageableProps),
        inputValues={f"property_{p.id}_mortgage_value": p.mortgageValue for p in mortgageableProps},
        procedure="Sum mortgage_value of unmortgaged undeveloped properties",
        unit="currency",
    )

    playerCash = ctx.playerCash(playerId)
    budget = sim.availableConstructionBudget(playerId)
    collector.add(
        f"construction_budget_{sideKey}_{playerId}",
        "available_construction_budget",
        f"Available construction budget for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=budget,
        inputReferences=(f"{bs}.players[{playerId}].cash",),
        inputValues={"cash": playerCash},
        formula="Cash + Mortgage Capacity",
        intermediateValues={"cash": playerCash, "mortgage_capacity": mc},
        unit="currency",
    )

    completedGroups: list[str] = []
    perGroupValues: list[dict[str, int | str]] = []
    unavailableGroups: list[str] = []

    for groupId in ctx.completedMonopolies(playerId):
        completedGroups.append(groupId)
        props = ctx.groupProperties(groupId)
        groupSize = len(props)
        build = sim.simulateGroupBuild(
            playerId,
            groupId,
            budget,
            ctx.availableHousesInBank(),
        )
        devMult = sim.developmentMultiplier(build.housesPerProperty)
        rent = resolver.maxAffordableRent(groupId, build.housesPerProperty, groupSize)
        if rent.status == RentResolution.UNAVAILABLE or rent.value is None:
            unavailableGroups.append(groupId)
            collector.add(
                f"monopoly_{sideKey}_{playerId}_{groupId}",
                "monopoly_value",
                f"Monopoly value for {groupId} ({side.value})",
                CalculationStatus.UNAVAILABLE,
                side,
                CalculationSubject(
                    playerIds=(playerId,),
                    groupIds=(groupId,),
                    propertyIds=tuple(p.id for p in props),
                ),
                missingInputs=("rent_table",),
                limitations=("Rent data unavailable at all source priority levels",),
            )
            continue

        mult, multSource = resolver.groupMultiplier(groupId)
        monoVal = int(rent.value * mult * devMult)
        assert total is not None
        total += monoVal
        perGroupValues.append({"group_id": groupId, "monopoly_value": monoVal})

        propIds = tuple(p.id for p in props)
        monoRefs = [f"{bs}.properties[{pid}].rent_table" for pid in propIds]
        if multSource == "GAME_CONFIGURATION":
            monoRefs.append(f"game_configuration.group_multipliers[{groupId}]")
        collector.add(
            f"monopoly_{sideKey}_{playerId}_{groupId}",
            "monopoly_value",
            f"Monopoly value for {groupId} ({side.value})",
            CalculationStatus.COMPLETE,
            side,
            CalculationSubject(
                playerIds=(playerId,),
                groupIds=(groupId,),
                propertyIds=propIds,
            ),
            result=monoVal,
            inputReferences=tuple(monoRefs),
            inputValues={
                "maximum_expected_rent": rent.value,
                "group_strategic_multiplier": mult,
            },
            formula="Maximum Expected Rent × Group Strategic Multiplier × Development Multiplier",
            intermediateValues={
                "maximum_expected_rent": rent.value,
                "group_strategic_multiplier": mult,
                "development_multiplier": devMult,
                "houses_per_property": build.housesPerProperty,
            },
            sources={
                "rent": rent.source,
                "group_multiplier": multSource,
                "development_multiplier": "SPECIFICATION_DEFAULT",
            },
            unit="currency",
        )

        cap = sim.evaluateCapability(playerId, groupId, "buildable")
        collector.add(
            f"dev_cap_buildable_{sideKey}_{playerId}_{groupId}",
            "development_capability",
            f"Buildable predicate for {groupId} ({side.value})",
            CalculationStatus.COMPLETE,
            side,
            CalculationSubject(playerIds=(playerId,), groupIds=(groupId,)),
            result=cap.result,
            intermediateValues={
                "predicate": "buildable",
                "houses_per_property": cap.housesPerProperty,
                "available_budget": cap.availableBudget,
                "unmortgage_cost": cap.unmortgageCost,
            },
            unit="boolean",
        )
        capD = sim.evaluateCapability(playerId, groupId, "dangerous")
        collector.add(
            f"dev_cap_dangerous_{sideKey}_{playerId}_{groupId}",
            "development_capability",
            f"Dangerous predicate for {groupId} ({side.value})",
            CalculationStatus.COMPLETE,
            side,
            CalculationSubject(playerIds=(playerId,), groupIds=(groupId,)),
            result=capD.result,
            intermediateValues={
                "predicate": "dangerous",
                "houses_per_property": capD.housesPerProperty,
                "available_budget": capD.availableBudget,
                "unmortgage_cost": capD.unmortgageCost,
            },
            unit="boolean",
        )

    totalKey = f"monopoly_total_{sideKey}_{playerId}"
    totalLimitations: tuple[str, ...]
    totalMissing: tuple[str, ...]
    if unavailableGroups and perGroupValues:
        totalStatus = CalculationStatus.PARTIAL
        totalLimitations = ("One or more completed monopolies lack rent data; total includes only known groups",)
        totalMissing = tuple(f"rent_table:{groupId}" for groupId in unavailableGroups)
    elif unavailableGroups and not perGroupValues:
        totalStatus = CalculationStatus.UNAVAILABLE
        totalLimitations = ("Rent data unavailable for every completed monopoly",)
        totalMissing = ("rent_table",)
        total = None
    else:
        totalStatus = CalculationStatus.COMPLETE
        totalLimitations = ()
        totalMissing = ()

    collector.add(
        totalKey,
        "monopoly_value",
        f"Total monopoly value for {playerId} ({side.value})",
        totalStatus,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=total,
        formula="Sum of per-group Monopoly Values",
        intermediateValues={
            "completed_groups": completedGroups,
            "per_group_values": perGroupValues,
            "total_monopoly_value": total if total is not None else 0,
            "unavailable_groups": unavailableGroups,
        },
        limitations=totalLimitations,
        missingInputs=totalMissing,
        unit="currency",
    )
    for groupId in completedGroups:
        collector.linkDependency(
            f"monopoly_{sideKey}_{playerId}_{groupId}",
            totalKey,
        )

    return total if total is not None else 0


def monopolyValueDelta(
    beforeCtx: BoardContext,
    afterCtx: BoardContext,
    playerId: str,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
) -> int:
    before = monopolyValueForSide(beforeCtx, playerId, CalculationSide.BEFORE, collector, defaults, "before")
    after = monopolyValueForSide(afterCtx, playerId, CalculationSide.AFTER, collector, defaults, "after")
    delta = after - before
    collector.add(
        f"monopoly_delta_{playerId}",
        "monopoly_value",
        f"Monopoly value delta for {playerId}",
        CalculationStatus.COMPLETE,
        CalculationSide.DELTA,
        CalculationSubject(playerIds=(playerId,)),
        result=delta,
        formula="after - before",
        intermediateValues={"before": before, "after": after},
        unit="currency",
    )
    collector.linkDependency(f"monopoly_total_before_{playerId}", f"monopoly_delta_{playerId}")
    collector.linkDependency(f"monopoly_total_after_{playerId}", f"monopoly_delta_{playerId}")
    return delta
