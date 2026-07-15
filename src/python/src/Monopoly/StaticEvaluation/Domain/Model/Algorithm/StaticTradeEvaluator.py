"""Orchestrates all 14 algorithm steps for the Static Trade Imbalance Evaluator."""

from __future__ import annotations

from Monopoly.StaticEvaluation.Domain.Model.Algorithm.Steps.Step01BaseAssetValue import (
    calculateBaseAssetValue,
)
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.Steps.Step02to04Monopoly import (
    monopolyValueDelta,
)
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.Steps.Step05HouseControl import (
    houseControlDelta,
)
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.Steps.Step06Railroads import railroadValueDelta
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.Steps.Step07Blocking import blockingValueDelta
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.Steps.Step08StrategicOpportunity import (
    strategicOpportunityDelta,
)
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.Steps.Step09RiskCoverage import (
    immediateRiskDelta,
)
from Monopoly.StaticEvaluation.Domain.Model.Algorithm.Steps.Step10to14Classification import (
    PlayerStrategicResult,
    applyInitiatorAdjustment,
    classifyFlags,
    computeStrategicValue,
    computeTradeRatio,
    evaluateFlags,
    publishClassification,
    publishStrategicValue,
)
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext
from Monopoly.StaticEvaluation.Domain.Model.EvaluationInput import EvaluationInput
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSide import CalculationSide
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationStatus import CalculationStatus
from Monopoly.StaticEvaluation.Domain.Model.Evidence.CalculationSubject import CalculationSubject
from Monopoly.StaticEvaluation.Domain.Model.Evidence.EvidenceCollector import EvidenceCollector
from Monopoly.StaticEvaluation.Domain.Model.Evidence.StaticAlgorithmEvidence import (
    StaticAlgorithmEvidence,
)
from Monopoly.StaticEvaluation.Domain.Model.SpecificationDefaults import (
    ALGORITHM_ID,
    ALGORITHM_NAME,
    ALGORITHM_VERSION,
    RISK_REFERENCE_ID,
    RISK_REFERENCE_VERSION,
    SpecificationDefaults,
)


class StaticTradeEvaluator:
    """Reference implementation of monopoly_static_algorithm v1.0."""

    def __init__(self, defaults: SpecificationDefaults | None = None) -> None:
        self._defaults = defaults or SpecificationDefaults()

    def evaluate(self, evaluationInput: EvaluationInput) -> StaticAlgorithmEvidence:
        collector = EvidenceCollector()
        trade = evaluationInput.trade
        participants = trade.participants

        if len(participants) != 2:
            return self._degradedEvidence(
                evaluationInput,
                collector,
                limitation="unsupported_participant_count",
                message=f"Trade has {len(participants)} participants; only two are supported",
            )

        if self._hasNonTradableTransfer(evaluationInput):
            collector.add(
                "non_tradable_error",
                "final_static_classification",
                "Non-tradable property transfer detected",
                CalculationStatus.ERROR,
                CalculationSide.TRADE,
                CalculationSubject(tradeId=trade.id),
                limitations=("Transferred property has is_tradable=false",),
            )
            return self._buildEvidence(
                evaluationInput,
                collector,
                finalConclusions={
                    "error": "NON_TRADABLE_PROPERTY_TRANSFER",
                    "classification": None,
                    "limitations": ["Non-tradable property in trade transfers"],
                },
            )

        playerA, playerB = participants[0], participants[1]
        beforeCtx = BoardContext(evaluationInput.boardStateBefore, evaluationInput.gameConfiguration)
        afterCtx = BoardContext(evaluationInput.boardStateAfter, evaluationInput.gameConfiguration)

        results: dict[str, PlayerStrategicResult] = {}
        riskLabels: dict[str, dict[str, str]] = {}
        riskWarnings: list[str] = []

        for playerId in (playerA, playerB):
            baseAsset = calculateBaseAssetValue(evaluationInput, playerId, collector, self._defaults)
            monopoly = monopolyValueDelta(beforeCtx, afterCtx, playerId, collector, self._defaults)
            houseControl, houseDenial = houseControlDelta(beforeCtx, afterCtx, playerId, collector, self._defaults)
            railroad = railroadValueDelta(beforeCtx, afterCtx, playerId, collector, self._defaults)
            blocking = blockingValueDelta(beforeCtx, afterCtx, playerId, collector, self._defaults)
            opportunity = strategicOpportunityDelta(beforeCtx, afterCtx, playerId, collector, self._defaults)
            riskChange, riskBefore, riskAfter = immediateRiskDelta(
                beforeCtx, afterCtx, playerId, collector, self._defaults
            )
            riskLabels[playerId] = {
                "before": riskBefore.riskLabel,
                "after": riskAfter.riskLabel,
            }
            riskWarnings.extend(riskAfter.warnings)

            partial = PlayerStrategicResult(
                playerId=playerId,
                baseAsset=baseAsset,
                monopoly=monopoly,
                houseControl=houseControl,
                houseDenial=houseDenial,
                railroad=railroad,
                blocking=blocking,
                opportunity=opportunity,
                immediateRiskChange=riskChange,
                strategicValue=0,
            )
            sv = computeStrategicValue(partial)
            partial = PlayerStrategicResult(
                playerId=playerId,
                baseAsset=baseAsset,
                monopoly=monopoly,
                houseControl=houseControl,
                houseDenial=houseDenial,
                railroad=railroad,
                blocking=blocking,
                opportunity=opportunity,
                immediateRiskChange=riskChange,
                strategicValue=sv,
            )
            publishStrategicValue(partial, collector)
            results[playerId] = partial

        values = {p: results[p].strategicValue for p in (playerA, playerB)}
        ratio = computeTradeRatio(values[playerA], values[playerB], playerA, playerB, collector, self._defaults)
        flags, ruleResults = evaluateFlags(evaluationInput, afterCtx, playerA, playerB, values, ratio, self._defaults)
        flagsBefore = set(flags)
        flags = applyInitiatorAdjustment(trade.initiatingPlayerId, values, flags)
        classification = classifyFlags(flags, self._defaults)
        publishClassification(
            flags,
            classification,
            collector,
            playerA,
            playerB,
            flagsBeforeAdjustment=flagsBefore,
            initiatingPlayerId=trade.initiatingPlayerId,
            ruleResults=ruleResults,
            ratio=ratio,
            values=values,
        )

        for pid in (playerA, playerB):
            svKey = f"strategic_value_{pid}"
            for side in ("before", "after"):
                collector.linkDependency(
                    f"mortgage_cap_{side}_{pid}",
                    f"construction_budget_{side}_{pid}",
                )
                collector.linkDependency(
                    f"mortgage_cap_{side}_{pid}",
                    f"avail_risk_res_{side}_{pid}",
                )
                collector.linkDependency(
                    f"house_control_{side}_{pid}",
                    f"house_control_delta_{pid}",
                )
                collector.linkDependency(
                    f"house_denial_{side}_{pid}",
                    f"house_denial_delta_{pid}",
                )
                collector.linkDependency(
                    f"railroad_{side}_{pid}",
                    f"railroad_delta_{pid}",
                )
                collector.linkDependency(
                    f"blocking_{side}_{pid}",
                    f"blocking_delta_{pid}",
                )
                collector.linkDependency(
                    f"strategic_opp_{side}_{pid}",
                    f"strategic_opp_delta_{pid}",
                )
                collector.linkDependency(
                    f"immediate_risk_{side}_{pid}",
                    f"immediate_risk_delta_{pid}",
                )
                collector.linkDependency(
                    f"avail_risk_res_{side}_{pid}",
                    f"immediate_risk_{side}_{pid}",
                )
            for _depType, depKey in [
                ("base_asset_value", f"base_asset_{pid}"),
                ("monopoly_delta", f"monopoly_delta_{pid}"),
                ("house_control_delta", f"house_control_delta_{pid}"),
                ("house_denial_delta", f"house_denial_delta_{pid}"),
                ("railroad_delta", f"railroad_delta_{pid}"),
                ("blocking_delta", f"blocking_delta_{pid}"),
                ("strategic_opp_delta", f"strategic_opp_delta_{pid}"),
                ("immediate_risk_delta", f"immediate_risk_delta_{pid}"),
            ]:
                collector.linkDependency(depKey, svKey)
            collector.linkDependency(svKey, "trade_ratio")
            for side in ("before", "after"):
                collector.linkDependency(
                    f"landing_exp_{side}_{pid}",
                    f"largest_threat_{side}_{pid}",
                )
                collector.linkDependency(
                    f"repair_exp_{side}_{pid}",
                    f"largest_threat_{side}_{pid}",
                )
                collector.linkDependency(
                    f"largest_threat_{side}_{pid}",
                    f"risk_margin_{side}_{pid}",
                )
                collector.linkDependency(
                    f"avail_risk_res_{side}_{pid}",
                    f"risk_margin_{side}_{pid}",
                )
                collector.linkDependency(
                    f"largest_threat_{side}_{pid}",
                    f"coverage_ratio_{side}_{pid}",
                )
                collector.linkDependency(
                    f"avail_risk_res_{side}_{pid}",
                    f"coverage_ratio_{side}_{pid}",
                )
                collector.linkDependency(
                    f"risk_margin_{side}_{pid}",
                    f"immediate_risk_{side}_{pid}",
                )
                collector.linkDependency(
                    f"coverage_ratio_{side}_{pid}",
                    f"immediate_risk_{side}_{pid}",
                )

        collector.linkDependency("trade_ratio", "final_classification")
        for pid in (playerA, playerB):
            collector.linkDependency(f"strategic_value_{pid}", "final_classification")

        calcIds = {
            playerA: collector.getId(f"strategic_value_{playerA}"),
            playerB: collector.getId(f"strategic_value_{playerB}"),
            "trade_ratio": collector.getId("trade_ratio"),
            "classification": collector.getId("final_classification"),
        }

        riskLabelConclusions: dict[str, dict[str, str | None]] = {}
        for pid in (playerA, playerB):
            riskLabelConclusions[pid] = {
                "before": riskLabels[pid]["before"],
                "after": riskLabels[pid]["after"],
                "before_calculation_id": collector.getId(f"immediate_risk_before_{pid}"),
                "after_calculation_id": collector.getId(f"immediate_risk_after_{pid}"),
            }

        riskWarningCalcIds = []
        for pid in (playerA, playerB):
            cid = collector.getId(f"immediate_risk_after_{pid}")
            if cid:
                riskWarningCalcIds.append(cid)

        finalConclusions = {
            "strategic_value": {
                playerA: {
                    "value": values[playerA],
                    "calculation_id": calcIds[playerA],
                },
                playerB: {
                    "value": values[playerB],
                    "calculation_id": calcIds[playerB],
                },
            },
            "trade_ratio": {
                "value": round(ratio, 2),
                "calculation_id": calcIds["trade_ratio"],
            },
            "flags": {
                "values": sorted(flags),
                "calculation_id": calcIds["classification"],
            },
            "risk_labels": riskLabelConclusions,
            "risk_warnings": {
                "values": sorted(set(riskWarnings)),
                "calculation_ids": riskWarningCalcIds,
            },
            "classification": classification,
            "classification_calculation_id": calcIds["classification"],
        }

        return self._buildEvidence(evaluationInput, collector, finalConclusions)

    def _hasNonTradableTransfer(self, evaluationInput: EvaluationInput) -> bool:
        props = {p.id: p for p in evaluationInput.boardStateBefore.properties}
        for transfer in evaluationInput.trade.transfers:
            if transfer.assetType != "property" or not transfer.assetId:
                continue
            prop = props.get(transfer.assetId)
            if prop and not prop.isTradable:
                return True
        return False

    def _degradedEvidence(
        self,
        evaluationInput: EvaluationInput,
        collector: EvidenceCollector,
        limitation: str,
        message: str,
    ) -> StaticAlgorithmEvidence:
        collector.add(
            limitation,
            "final_static_classification",
            message,
            CalculationStatus.ERROR,
            CalculationSide.TRADE,
            CalculationSubject(tradeId=evaluationInput.trade.id),
            limitations=(message,),
        )
        return self._buildEvidence(
            evaluationInput,
            collector,
            finalConclusions={
                "classification": None,
                "limitations": [message],
            },
        )

    def _buildEvidence(
        self,
        evaluationInput: EvaluationInput,
        collector: EvidenceCollector,
        finalConclusions: dict,
    ) -> StaticAlgorithmEvidence:
        return StaticAlgorithmEvidence(
            id=evaluationInput.evidenceId,
            algorithmId=ALGORITHM_ID,
            algorithmName=ALGORITHM_NAME,
            algorithmVersion=ALGORITHM_VERSION,
            purpose="trade ratio calculation and competitive advantage calculation",
            intermediateCalculations=tuple(collector.items),
            finalConclusions=finalConclusions,
            metadata={
                "implementation_overrides": [],
                "specification_dependencies": [
                    {
                        "specification_id": RISK_REFERENCE_ID,
                        "specification_version": RISK_REFERENCE_VERSION,
                    }
                ],
            },
            statistics={"calculation_count": collector.calcIds.count},
        )
