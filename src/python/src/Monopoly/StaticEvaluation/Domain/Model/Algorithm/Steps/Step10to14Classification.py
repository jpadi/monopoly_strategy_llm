"""Steps 10–14: Trade initiator, strategic value, ratio, flags, classification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from Monopoly.StaticEvaluation.Domain.Model.Algorithm.DevelopmentSimulator import DevelopmentSimulator
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import EvaluationInput
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.EvidenceCollector import EvidenceCollector
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import SpecificationDefaults


@dataclass(frozen=True, slots=True)
class PlayerStrategicResult:
    playerId: str
    baseAsset: int
    monopoly: int
    houseControl: int
    houseDenial: int
    railroad: int
    blocking: int
    opportunity: int
    immediateRiskChange: int
    strategicValue: int


def computeStrategicValue(result: PlayerStrategicResult) -> int:
    raw = (
        result.baseAsset
        + result.monopoly
        + result.houseControl
        + result.houseDenial
        + result.railroad
        + result.blocking
        + result.opportunity
        - result.immediateRiskChange
    )
    return max(0, raw)


def publishStrategicValue(
    result: PlayerStrategicResult,
    collector: EvidenceCollector,
) -> None:
    collector.add(
        f"strategic_value_{result.playerId}",
        "strategic_value",
        f"Strategic value for {result.playerId}",
        CalculationStatus.COMPLETE,
        CalculationSide.TRADE,
        CalculationSubject(playerIds=(result.playerId,)),
        result=result.strategicValue,
        intermediateValues={
            "base_asset_value": result.baseAsset,
            "monopoly_value": result.monopoly,
            "house_control_bonus": result.houseControl,
            "house_denial_bonus": result.houseDenial,
            "railroad_value": result.railroad,
            "blocking_value": result.blocking,
            "strategic_opportunity_value": result.opportunity,
            "immediate_risk_change": result.immediateRiskChange,
            "floor_applied": result.strategicValue == 0
            and (
                result.baseAsset
                + result.monopoly
                + result.houseControl
                + result.houseDenial
                + result.railroad
                + result.blocking
                + result.opportunity
                - result.immediateRiskChange
            )
            < 0,
        },
        formula=(
            "Base + Monopoly + House Control + House Denial + Railroad + Blocking + Opportunity - Immediate Risk Change"
        ),
        unit="currency",
    )


def computeTradeRatio(
    valueA: int,
    valueB: int,
    playerA: str,
    playerB: str,
    collector: EvidenceCollector,
    defaults: SpecificationDefaults,
) -> float:
    highest = max(valueA, valueB)
    lowest = max(1, min(valueA, valueB))
    rawRatio = highest / lowest
    publishedRatio = min(rawRatio, defaults.maxTradeRatio)
    collector.add(
        "trade_ratio",
        "trade_ratio",
        "Trade ratio comparison",
        CalculationStatus.COMPLETE,
        CalculationSide.TRADE,
        CalculationSubject(playerIds=(playerA, playerB)),
        result=round(publishedRatio, 2),
        intermediateValues={
            "highest_strategic_value": highest,
            "lowest_strategic_value": lowest,
            "division_denominator": lowest,
            "raw_trade_ratio": rawRatio,
            "maximum_trade_ratio": defaults.maxTradeRatio,
            "published_trade_ratio": round(publishedRatio, 2),
        },
        formula="min(max(A,B) / max(1, min(A,B)), MAX_TRADE_RATIO)",
        unit="ratio",
    )
    return publishedRatio


def evaluateFlags(
    evaluationInput: EvaluationInput,
    afterCtx: BoardContext,
    playerA: str,
    playerB: str,
    values: dict[str, int],
    ratio: float,
    defaults: SpecificationDefaults,
) -> tuple[set[str], list[dict[str, Any]]]:
    flags: set[str] = set()
    ruleResults: list[dict[str, Any]] = []
    sim = DevelopmentSimulator(afterCtx, defaults)

    highlySuspicious = ratio >= defaults.tradeRatioSuspicious
    suspicious = (not highlySuspicious) and ratio >= defaults.tradeRatioSlightlyUnbalanced
    if highlySuspicious:
        flags.add("HIGHLY_SUSPICIOUS_IMBALANCE")
    elif suspicious:
        flags.add("SUSPICIOUS_IMBALANCE")
    ruleResults.append(
        {
            "rule": "HIGHLY_SUSPICIOUS_IMBALANCE",
            "ratio": round(ratio, 2),
            "threshold": defaults.tradeRatioSuspicious,
            "predicate_result": highlySuspicious,
            "flag_generated": "HIGHLY_SUSPICIOUS_IMBALANCE" if highlySuspicious else None,
        }
    )
    ruleResults.append(
        {
            "rule": "SUSPICIOUS_IMBALANCE",
            "ratio": round(ratio, 2),
            "threshold": defaults.tradeRatioSlightlyUnbalanced,
            "predicate_result": suspicious,
            "flag_generated": "SUSPICIOUS_IMBALANCE" if suspicious else None,
        }
    )

    buildableResult = False
    for receiver in (playerA, playerB):
        giver = playerB if receiver == playerA else playerA
        for gid in afterCtx.completedMonopolies(receiver):
            if gid not in afterCtx.completedMonopolies(giver):
                cap = sim.evaluateCapability(receiver, gid, "buildable")
                otherVal = values[giver]
                receiverVal = values[receiver]
                if cap.result and otherVal < receiverVal * defaults.flagCompensationThresholdRatio:
                    buildableResult = True
                    flags.add("BUILDABLE_MONOPOLY_GIVEN_AWAY")
    ruleResults.append(
        {
            "rule": "BUILDABLE_MONOPOLY_GIVEN_AWAY",
            "predicate_result": buildableResult,
            "flag_generated": "BUILDABLE_MONOPOLY_GIVEN_AWAY" if buildableResult else None,
        }
    )

    dangerousResult = False
    beforeCtx = BoardContext(evaluationInput.boardStateBefore, evaluationInput.gameConfiguration)
    for playerId in (playerA, playerB):
        for gid in afterCtx.completedMonopolies(playerId):
            if gid not in beforeCtx.completedMonopolies(playerId):
                cap = sim.evaluateCapability(playerId, gid, "dangerous")
                if cap.result:
                    dangerousResult = True
                    flags.add("DANGEROUS_MONOPOLY_ENABLED")
    ruleResults.append(
        {
            "rule": "DANGEROUS_MONOPOLY_ENABLED",
            "predicate_result": dangerousResult,
            "flag_generated": "DANGEROUS_MONOPOLY_ENABLED" if dangerousResult else None,
        }
    )

    high = max(values[playerA], values[playerB])
    low = min(values[playerA], values[playerB])
    symbolicResult = high > 0 and low < high * defaults.symbolicCompensationThresholdRatio
    if symbolicResult:
        flags.add("SYMBOLIC_VALUE_TRADE")
    ruleResults.append(
        {
            "rule": "SYMBOLIC_VALUE_TRADE",
            "highest_value": high,
            "lowest_value": low,
            "threshold_ratio": defaults.symbolicCompensationThresholdRatio,
            "predicate_result": symbolicResult,
            "flag_generated": "SYMBOLIC_VALUE_TRADE" if symbolicResult else None,
        }
    )

    houseControlResult = False
    for receiver in (playerA, playerB):
        giver = playerB if receiver == playerA else playerA
        simResult = sim.simulateAllMonopolies(receiver)
        if simResult.totalHousesControlled >= 24:
            if values[giver] < values[receiver] * defaults.flagCompensationThresholdRatio:
                houseControlResult = True
                flags.add("HOUSE_CONTROL_ENABLED")
    ruleResults.append(
        {
            "rule": "HOUSE_CONTROL_ENABLED",
            "predicate_result": houseControlResult,
            "flag_generated": "HOUSE_CONTROL_ENABLED" if houseControlResult else None,
        }
    )

    houseDenialResult = False
    for playerId in (playerA, playerB):
        simResult = sim.simulateAllMonopolies(playerId)
        if simResult.remainingHousesInBank <= 4:
            houseDenialResult = True
            flags.add("HOUSE_SUPPLY_DENIAL")
    ruleResults.append(
        {
            "rule": "HOUSE_SUPPLY_DENIAL",
            "predicate_result": houseDenialResult,
            "flag_generated": "HOUSE_SUPPLY_DENIAL" if houseDenialResult else None,
        }
    )

    railroadResult = False
    if afterCtx.mostlyBlockedBoard():
        for receiver in (playerA, playerB):
            giver = playerB if receiver == playerA else playerA
            if afterCtx.railroadCount(receiver) == 4 and afterCtx.railroadCount(giver) < 4:
                if values[giver] < values[receiver] * defaults.flagCompensationThresholdRatio:
                    railroadResult = True
                    flags.add("STRATEGIC_RAILROAD_GIVEAWAY")
    ruleResults.append(
        {
            "rule": "STRATEGIC_RAILROAD_GIVEAWAY",
            "predicate_result": railroadResult,
            "flag_generated": "STRATEGIC_RAILROAD_GIVEAWAY" if railroadResult else None,
        }
    )

    return flags, ruleResults


def applyInitiatorAdjustment(
    tradeInitiator: str,
    values: dict[str, int],
    flags: set[str],
) -> set[str]:
    apparentOverpayer = min(values, key=lambda p: values[p])
    if apparentOverpayer != tradeInitiator:
        return flags
    adjusted = set(flags)
    if "HIGHLY_SUSPICIOUS_IMBALANCE" in adjusted:
        adjusted.remove("HIGHLY_SUSPICIOUS_IMBALANCE")
        adjusted.add("SUSPICIOUS_IMBALANCE")
    elif "SUSPICIOUS_IMBALANCE" in adjusted:
        adjusted.remove("SUSPICIOUS_IMBALANCE")
    return adjusted


def classifyFlags(flags: set[str], defaults: SpecificationDefaults) -> str:
    strong = defaults.strongFlags
    strongCount = len(flags & strong)
    if strongCount >= 3:
        return "REVIEW_RECOMMENDED"
    if strongCount >= 2:
        return "STRONG_FLAG"
    if strongCount >= 1:
        return "SOFT_FLAG"
    if "SUSPICIOUS_IMBALANCE" in flags:
        return "SOFT_FLAG"
    return "NO_FLAG"


def publishClassification(
    flags: set[str],
    classification: str,
    collector: EvidenceCollector,
    playerA: str,
    playerB: str,
    flagsBeforeAdjustment: set[str],
    initiatingPlayerId: str = "",
    ruleResults: list[dict[str, Any]] | None = None,
    ratio: float = 0.0,
    values: dict[str, int] | None = None,
) -> None:
    adjustmentApplied = flags != flagsBeforeAdjustment
    strongFlags = SpecificationDefaults().strongFlags
    activeStrong = sorted(flags & strongFlags)
    apparentOverpayer: str | None = None
    if values:
        apparentOverpayer = min(values, key=lambda p: values[p])

    collector.add(
        "final_classification",
        "final_static_classification",
        "Final static trade classification",
        CalculationStatus.COMPLETE,
        CalculationSide.TRADE,
        CalculationSubject(playerIds=(playerA, playerB)),
        result=classification,
        inputReferences=("trade.initiating_player_id",),
        inputValues={"initiating_player_id": initiatingPlayerId},
        procedure=("Evaluate automatic flag rules, apply initiator adjustment, classify by strong-flag count"),
        intermediateValues={
            "automatic_rules": ruleResults or [],
            "flags_before_initiator_adjustment": sorted(flagsBeforeAdjustment),
            "flags_after_initiator_adjustment": sorted(flags),
            "initiator_rule_evaluated": True,
            "initiating_player_id": initiatingPlayerId,
            "apparent_overpayer": apparentOverpayer,
            "initiator_adjustment_applied": adjustmentApplied,
            "strong_flags": activeStrong,
            "strong_flag_count": len(activeStrong),
            "trade_ratio": round(ratio, 2),
            "final_classification": classification,
        },
        unit="classification",
    )
