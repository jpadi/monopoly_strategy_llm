"""Step 9 — Immediate Risk (Risk Coverage)."""

from __future__ import annotations

from dataclasses import dataclass

from Monopoly.StaticEvaluation.Domain.Model.Algorithm.DevelopmentSimulator import DevelopmentSimulator
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.RentResolver import RentResolution, RentResolver
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.EvidenceCollector import EvidenceCollector
from Monopoly.StaticEvaluation.Domain.Model.RiskReference.ClassicRiskReference import (
    ClassicRiskReference,
)
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import (
    RAILROAD_GROUP,
    UTILITY_GROUP,
    SpecificationDefaults,
)
from Monopoly.StaticEvaluation.Domain.Model.ValueSource import ValueSourceLabel


@dataclass(frozen=True, slots=True)
class RiskSideResult:
    riskPenalty: int
    riskLabel: str
    riskMargin: int
    repairExposure: int
    availableResources: int
    largestThreat: int
    coverageRatio: float | None
    noExposure: bool
    warnings: tuple[str, ...]


def _ratioGte(resources: int, threat: int, num: int, den: int) -> bool:
    if threat <= 0:
        return True
    return num * resources >= den * threat


@dataclass(frozen=True, slots=True)
class RiskPenaltyDetail:
    penalty: int
    ratio: float | None
    noExposure: bool
    surplus: int
    deficit: int
    ratioComponent: int
    surplusOrDeficitComponent: int
    ratioTier: str
    surplusOrDeficitTier: str
    uncapped: int
    minimum: int
    maximum: int


def _computeRiskPenalty(
    resources: int,
    threat: int,
    defaults: SpecificationDefaults,
) -> RiskPenaltyDetail:
    margin = resources - threat
    surplus = max(margin, 0)
    deficit = max(-margin, 0)
    minPenalty = defaults.riskPenaltyMin
    maxPenalty = defaults.riskPenaltyMax

    if threat == 0 and resources >= 0:
        ratio: float | None = None
        noExposure = True
        ratioCushion = defaults.ratioCushionHigh
        surplusCushion = 0
        if surplus >= 2000:
            surplusCushion = 250
        elif surplus >= 1000:
            surplusCushion = 150
        elif surplus >= 500:
            surplusCushion = 100
        uncapped = -(ratioCushion + surplusCushion)
        penalty = max(minPenalty, uncapped)
        return RiskPenaltyDetail(
            penalty,
            ratio,
            noExposure,
            surplus,
            deficit,
            -ratioCushion,
            -surplusCushion,
            "NO_EXPOSURE",
            f"surplus>={surplus}",
            uncapped,
            minPenalty,
            maxPenalty,
        )

    noExposure = False
    ratio = round(resources / threat, 2) if threat > 0 else None

    if margin < 0 and threat > 0:
        if not _ratioGte(resources, threat, 2, 1):
            ratioSeverity = defaults.ratioSeverityLow
            ratioTier = "ratio<0.5"
        elif not _ratioGte(resources, threat, 1, 1):
            ratioSeverity = defaults.ratioSeverityMid
            ratioTier = "0.5<=ratio<1.0"
        else:
            ratioSeverity = 0
            ratioTier = "ratio>=1.0"
        deficitSeverity = 0
        deficitTier = "deficit<min_threshold"
        for threshold, sev in defaults.deficitSeverityTiers:
            if deficit >= threshold:
                deficitSeverity = sev
                deficitTier = f"deficit>={threshold}"
                break
        uncapped = ratioSeverity + deficitSeverity
        penalty = min(maxPenalty, uncapped)
        return RiskPenaltyDetail(
            penalty,
            ratio,
            noExposure,
            surplus,
            deficit,
            ratioSeverity,
            deficitSeverity,
            ratioTier,
            deficitTier,
            uncapped,
            minPenalty,
            maxPenalty,
        )

    ratioCushion = 0
    ratioTier = "ratio<1.25"
    if ratio is not None and _ratioGte(resources, threat, 1, 2):
        ratioCushion = defaults.ratioCushionHigh
        ratioTier = "ratio>=2.0"
    elif ratio is not None and _ratioGte(resources, threat, 4, 5):
        ratioCushion = defaults.ratioCushionMid
        ratioTier = "ratio>=1.25"

    surplusCushion = 0
    surplusTier = "surplus<min_threshold"
    for threshold, cushion in defaults.surplusCushionTiers:
        if surplus >= threshold:
            surplusCushion = cushion
            surplusTier = f"surplus>={threshold}"
            break

    uncapped = -(ratioCushion + surplusCushion)
    penalty = max(minPenalty, uncapped)
    return RiskPenaltyDetail(
        penalty,
        ratio,
        noExposure,
        surplus,
        deficit,
        -ratioCushion,
        -surplusCushion,
        ratioTier,
        surplusTier,
        uncapped,
        minPenalty,
        maxPenalty,
    )


def _riskLabel(penalty: int) -> str:
    if penalty >= 900:
        return "SURVIVAL_RISK_CRITICAL"
    if penalty >= 600:
        return "SURVIVAL_RISK_HIGH"
    if penalty > 0:
        return "SURVIVAL_RISK_MODERATE"
    if penalty == 0:
        return "SURVIVAL_RISK_LOW"
    return "SURVIVAL_RISK_VERY_LOW"


@dataclass(frozen=True, slots=True)
class LandingExposureResult:
    maxRent: int
    threatProp: str | None
    threatOpponent: str | None
    multiLanding: dict[str, list[int]]
    rentSource: ValueSourceLabel


def _landingExposure(ctx: BoardContext, playerId: str) -> LandingExposureResult:
    resolver = RentResolver(ctx)
    maxRent = 0
    threatProp: str | None = None
    threatOpponent: str | None = None
    multiEvidence: dict[str, list[int]] = {}
    rentSource = ValueSourceLabel.UNAVAILABLE

    for prop in ctx.properties.values():
        owner = prop.ownerPlayerId
        if owner is None or owner == playerId:
            continue
        if prop.isMortgaged:
            continue

        rent = 0
        resolved = None
        if prop.category == "street":
            if not ctx.ownsGroup(owner, prop.groupId):
                continue
            resolved = resolver.streetRent(prop, useMaxInGroup=True)
            if resolved.status == RentResolution.UNAVAILABLE or resolved.value is None:
                continue
            rent = resolved.value
            if resolved.multiLanding:
                multiEvidence[prop.id] = list(resolved.multiLanding)
        elif prop.groupId == RAILROAD_GROUP:
            resolved = resolver.railroadRent(owner, prop)
            if resolved.value is not None:
                rent = resolved.value
                if resolved.multiLanding:
                    multiEvidence[prop.id] = list(resolved.multiLanding)
        elif prop.groupId == UTILITY_GROUP:
            resolved = resolver.utilityRent(owner, prop)
            if resolved.value is not None:
                rent = resolved.value
                if resolved.multiLanding:
                    multiEvidence[prop.id] = list(resolved.multiLanding)

        if rent > maxRent:
            maxRent = rent
            threatProp = prop.id
            threatOpponent = owner
            if resolved is not None:
                rentSource = resolved.source

    return LandingExposureResult(maxRent, threatProp, threatOpponent, multiEvidence, rentSource)


def evaluateRiskSide(
    ctx: BoardContext,
    playerId: str,
    side: CalculationSide,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
    sideKey: str,
) -> RiskSideResult:
    sim = DevelopmentSimulator(ctx, defaults)
    cash = ctx.playerCash(playerId)
    mortgageCap = sim.mortgageCapacity(playerId)
    buildingLiq = sim.buildingLiquidationValue(playerId)
    mandatory = 0
    resources = cash + mortgageCap + buildingLiq - mandatory

    mortgageableProps = [
        p for p in ctx.playerProperties(playerId) if not p.isMortgaged and p.houses == 0 and not p.hasHotel
    ]
    developedProps = [p for p in ctx.playerProperties(playerId) if p.houses > 0 or p.hasHotel]

    houses = sum(p.houses for p in ctx.playerProperties(playerId) if p.category == "street")
    hotels = sum(1 for p in ctx.playerProperties(playerId) if p.hasHotel)
    repair = ClassicRiskReference.repairExposureBothCards(houses, hotels)

    landingResult = _landingExposure(ctx, playerId)
    landing = landingResult.maxRent
    threatProp = landingResult.threatProp
    threatOpponent = landingResult.threatOpponent
    multiLanding = landingResult.multiLanding
    threat = landing + repair

    bs = f"board_state_{sideKey}"
    riskInputRefs = [f"{bs}.players[{playerId}].cash"]
    riskInputRefs.extend(f"{bs}.properties[{p.id}].mortgage_value" for p in mortgageableProps)
    for prop in developedProps:
        riskInputRefs.append(f"{bs}.properties[{prop.id}].houses")
        if prop.hasHotel:
            riskInputRefs.append(f"{bs}.properties[{prop.id}].has_hotel")
    riskInputRefs.append("game_configuration.house_sell_back_ratio")
    riskInputRefs.append("game_configuration.hotel_sell_back_ratio")

    collector.add(
        f"avail_risk_res_{sideKey}_{playerId}",
        "available_risk_resources",
        f"Available risk resources for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(
            playerIds=(playerId,),
            propertyIds=tuple(p.id for p in mortgageableProps + developedProps),
        ),
        result=resources,
        inputReferences=tuple(riskInputRefs),
        inputValues={
            "cash": cash,
            "eligible_mortgage_property_ids": [p.id for p in mortgageableProps],
            "eligible_mortgage_values": {p.id: p.mortgageValue for p in mortgageableProps},
        },
        formula="Cash + Mortgage Capacity + Building Liquidation - Mandatory Costs",
        intermediateValues={
            "mortgage_capacity": mortgageCap,
            "building_liquidation": buildingLiq,
            "mandatory_costs": mandatory,
        },
        unit="currency",
    )
    landingRefs: tuple[str, ...] = ()
    landingIvs: dict[str, int] = {}
    if threatProp:
        if landingResult.rentSource == ValueSourceLabel.BOARD_STATE_RENT_TABLE:
            landingRefs = (f"{bs}.properties[{threatProp}].rent_table",)
        else:
            landingRefs = (f"{bs}.properties[{threatProp}].owner_player_id",)
        landingIvs["threat_collectible_rent"] = landing
    collector.add(
        f"landing_exp_{sideKey}_{playerId}",
        "landing_exposure",
        f"Landing exposure for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(
            playerIds=(playerId,),
            propertyIds=(threatProp,) if threatProp else (),
        ),
        result=landing,
        inputReferences=landingRefs,
        inputValues=landingIvs,
        intermediateValues={
            "threat_property_id": threatProp,
            "threat_opponent_id": threatOpponent,
            "multi_landing_exposures": multiLanding,
        },
        sources={"rent": landingResult.rentSource},
        procedure=(
            "Select the highest currently collectible rent from opponent-owned"
            " unmortgaged properties using the configured source priority"
        ),
        unit="currency",
    )
    collector.add(
        f"repair_exp_{sideKey}_{playerId}",
        "repair_exposure",
        f"Repair exposure for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=repair,
        inputReferences=(f"{bs}.players[{playerId}].owned_properties",),
        inputValues={"houses": houses, "hotels": hotels},
        procedure=("Houses x house repair cost + Hotels x hotel repair cost under the Both Cards repair-card scenario"),
        intermediateValues={
            "houses": houses,
            "hotels": hotels,
            "repair_card_scenario": "Both Cards",
        },
        sources={"repair_table": ValueSourceLabel.RISK_REFERENCE_DEFAULT},
        unit="currency",
    )
    collector.add(
        f"largest_threat_{sideKey}_{playerId}",
        "largest_threat",
        f"Largest threat for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=threat,
        formula="Landing Exposure + Repair Exposure",
        intermediateValues={
            "landing_exposure": landing,
            "repair_exposure": repair,
        },
        unit="currency",
    )

    rpd = _computeRiskPenalty(resources, threat, defaults)
    penalty = rpd.penalty
    ratio = rpd.ratio
    noExposure = rpd.noExposure
    margin = resources - threat
    surplus = rpd.surplus
    deficit = rpd.deficit
    label = _riskLabel(penalty)

    limitations: tuple[str, ...] = ("NO_EXPOSURE",) if noExposure else ()
    collector.add(
        f"risk_margin_{sideKey}_{playerId}",
        "risk_margin",
        f"Risk margin for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=margin,
        formula="Available Risk Resources - Largest Threat",
        intermediateValues={
            "available_risk_resources": resources,
            "largest_threat": threat,
            "surplus_amount": surplus,
            "deficit_amount": deficit,
        },
        unit="currency",
    )
    collector.add(
        f"coverage_ratio_{sideKey}_{playerId}",
        "coverage_ratio",
        f"Coverage ratio for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=ratio,
        formula="Available Risk Resources / Largest Threat",
        intermediateValues={
            "available_risk_resources": resources,
            "largest_threat": threat,
            "no_exposure": noExposure,
        },
        limitations=limitations,
        unit="ratio",
    )
    warnings: list[str] = []
    if side == CalculationSide.AFTER:
        if margin < 0:
            warnings.append("PLAYER_CANNOT_SURVIVE_ONE_LANDING")
        if resources < repair:
            warnings.append("PLAYER_CANNOT_COVER_REPAIR_EXPOSURE")

    collector.add(
        f"immediate_risk_{sideKey}_{playerId}",
        "immediate_risk",
        f"Risk penalty for {playerId} ({side.value})",
        CalculationStatus.COMPLETE,
        side,
        CalculationSubject(playerIds=(playerId,)),
        result=penalty,
        procedure=(
            "Signed sum of the applicable Coverage Ratio tier"
            " and the applicable Surplus or Deficit tier,"
            " bounded by the normative minimum and maximum"
        ),
        intermediateValues={
            "available_risk_resources": resources,
            "largest_threat": threat,
            "risk_margin": margin,
            "coverage_ratio": ratio,
            "coverage_ratio_tier": rpd.ratioTier,
            "coverage_ratio_component": rpd.ratioComponent,
            "surplus_or_deficit_amount": surplus if surplus > 0 else -deficit,
            "surplus_or_deficit_tier": rpd.surplusOrDeficitTier,
            "surplus_or_deficit_component": rpd.surplusOrDeficitComponent,
            "uncapped_risk_penalty": rpd.uncapped,
            "minimum_risk_penalty": rpd.minimum,
            "maximum_risk_penalty": rpd.maximum,
            "bounded_risk_penalty": penalty,
            "risk_label": label,
            "warnings": warnings,
        },
        unit="currency",
    )

    return RiskSideResult(
        riskPenalty=penalty,
        riskLabel=label,
        riskMargin=margin,
        repairExposure=repair,
        availableResources=resources,
        largestThreat=threat,
        coverageRatio=ratio,
        noExposure=noExposure,
        warnings=tuple(warnings),
    )


def immediateRiskDelta(
    beforeCtx: BoardContext,
    afterCtx: BoardContext,
    playerId: str,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
) -> tuple[int, RiskSideResult, RiskSideResult]:
    before = evaluateRiskSide(beforeCtx, playerId, CalculationSide.BEFORE, collector, defaults, "before")
    after = evaluateRiskSide(afterCtx, playerId, CalculationSide.AFTER, collector, defaults, "after")
    delta = after.riskPenalty - before.riskPenalty
    collector.add(
        f"immediate_risk_delta_{playerId}",
        "immediate_risk",
        f"Immediate risk change for {playerId}",
        CalculationStatus.COMPLETE,
        CalculationSide.DELTA,
        CalculationSubject(playerIds=(playerId,)),
        result=delta,
        formula="Risk Penalty After - Risk Penalty Before",
        intermediateValues={"before": before.riskPenalty, "after": after.riskPenalty},
        unit="currency",
    )
    return delta, before, after
