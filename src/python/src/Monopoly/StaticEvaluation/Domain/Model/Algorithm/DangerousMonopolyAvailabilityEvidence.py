"""Evidence assembly for Dangerous Monopoly Availability predicate."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.Algorithm.DevelopmentSimulator import DevelopmentSimulator
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext


@dataclass(frozen=True, slots=True)
class DangerousMonopolyAvailabilityEvidence:
    result: bool
    inputValues: dict[str, Any]
    intermediateValues: dict[str, Any]
    inputReferences: tuple[str, ...]


def _isMortgageEligible(prop) -> bool:
    return not prop.isMortgaged and prop.houses == 0 and not prop.hasHotel


def buildDangerousMonopolyAvailabilityEvidence(
    ctx: BoardContext,
    opponentId: str,
    groupId: str,
    *,
    boardStateKey: str,
) -> DangerousMonopolyAvailabilityEvidence:
    """Build auditable evidence for one opponent/group availability determination."""
    groupProps = ctx.groupProperties(groupId)
    bs = boardStateKey

    ownedByPlayer: list[str] = []
    unownedProperties: list[str] = []
    ownedByOtherPlayers: list[str] = []
    overrides: dict[str, str | None] = {}
    candidateGroupMortgageValues: dict[str, int] = {}

    inputRefs: list[str] = []
    for prop in groupProps:
        candidateGroupMortgageValues[prop.id] = prop.mortgageValue
        inputRefs.append(f"{bs}.properties[{prop.id}].owner_player_id")
        inputRefs.append(f"{bs}.properties[{prop.id}].mortgage_value")
        inputRefs.append(f"{bs}.properties[{prop.id}].is_mortgaged")
        inputRefs.append(f"{bs}.properties[{prop.id}].house_cost")
        if prop.ownerPlayerId == opponentId:
            ownedByPlayer.append(prop.id)
        elif prop.ownerPlayerId is None:
            unownedProperties.append(prop.id)
            overrides[prop.id] = opponentId
        else:
            ownedByOtherPlayers.append(prop.id)

    houseCost = groupProps[0].houseCost if groupProps else 0
    playerCash = ctx.playerCash(opponentId)
    availableHouses = ctx.availableHousesInBank()
    config = ctx.config

    inputValues: dict[str, Any] = {
        "player_cash": playerCash,
        "available_houses": availableHouses,
        "candidate_group_house_cost": houseCost,
        "candidate_group_property_ids": [p.id for p in groupProps],
        "owned_by_player": sorted(ownedByPlayer),
        "owned_by_other_players": sorted(ownedByOtherPlayers),
        "unowned_properties": sorted(unownedProperties),
        "candidate_group_mortgage_values": candidateGroupMortgageValues,
        "building_allowed_with_mortgaged_group_member": config.buildingAllowedWithMortgagedGroupMember,
        "mortgage_interest_rate": config.mortgageInterestRate,
        "even_building_required": config.evenBuildingRequired,
    }

    inputRefs.append(f"{bs}.players[{opponentId}].cash")
    inputRefs.append(f"{bs}.game_state.available_houses")
    inputRefs.append("game_configuration.building_allowed_with_mortgaged_group_member")
    inputRefs.append("game_configuration.mortgage_interest_rate")
    inputRefs.append("game_configuration.even_building_required")

    intermediateValues: dict[str, Any] = {
        "hypothetical_assignment": dict(sorted(overrides.items())),
        "excluded_candidate_group_properties": sorted(p.id for p in groupProps),
        "eligible_mortgageable_property_ids": [],
        "eligible_external_mortgage_capacity": 0,
        "available_construction_budget": 0,
        "unmortgage_prerequisite_cost": 0,
        "mandatory_immediate_costs": 0,
        "maximum_even_buildable_houses": 0,
        "houses_per_property": 0,
        "dangerous_predicate": False,
        "final_result": False,
    }

    if ownedByOtherPlayers:
        intermediateValues["dangerous_predicate"] = False
        intermediateValues["final_result"] = False
        intermediateValues["reason"] = "other_player_owns_group_property"
        return DangerousMonopolyAvailabilityEvidence(
            result=False,
            inputValues=inputValues,
            intermediateValues=intermediateValues,
            inputReferences=tuple(inputRefs),
        )

    hypCtx = ctx if not overrides else BoardContext.withHypotheticalOwnership(ctx.board, ctx.config, overrides)

    if not hypCtx.ownsGroup(opponentId, groupId):
        intermediateValues["dangerous_predicate"] = False
        intermediateValues["final_result"] = False
        intermediateValues["reason"] = "group_not_completable"
        return DangerousMonopolyAvailabilityEvidence(
            result=False,
            inputValues=inputValues,
            intermediateValues=intermediateValues,
            inputReferences=tuple(inputRefs),
        )

    eligibleOutside = [
        p.id for p in hypCtx.playerProperties(opponentId) if p.groupId != groupId and _isMortgageEligible(p)
    ]
    for propId in eligibleOutside:
        inputRefs.append(f"{bs}.properties[{propId}].mortgage_value")

    sim = DevelopmentSimulator(hypCtx)
    externalMortgage = sim.mortgageCapacity(opponentId, excludeGroupId=groupId)
    unmortgageCost = sim.unmortgageCostForGroup(opponentId, groupId)
    budget = playerCash + externalMortgage
    build = sim.simulateGroupBuild(opponentId, groupId, budget, availableHouses)
    dangerous = build.dangerous
    groupSize = len(groupProps)

    intermediateValues.update(
        {
            "eligible_mortgageable_property_ids": sorted(eligibleOutside),
            "eligible_external_mortgage_capacity": externalMortgage,
            "available_construction_budget": budget,
            "unmortgage_prerequisite_cost": unmortgageCost,
            "mandatory_immediate_costs": 0,
            "maximum_even_buildable_houses": build.housesPerProperty * groupSize,
            "houses_per_property": build.housesPerProperty,
            "dangerous_predicate": dangerous,
            "final_result": dangerous,
        }
    )

    return DangerousMonopolyAvailabilityEvidence(
        result=dangerous,
        inputValues=inputValues,
        intermediateValues=intermediateValues,
        inputReferences=tuple(inputRefs),
    )
