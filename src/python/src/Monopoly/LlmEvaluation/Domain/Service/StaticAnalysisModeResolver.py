"""Deterministic pre-LLM runtime mode resolution."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Model.Input.JudgeInput import JudgeInput
from Monopoly.LlmEvaluation.Domain.Model.JudgeEnums import (
    EvidenceSource,
    EvidenceUsability,
    ExecutionStatus,
    RuntimeExecutionMode,
    StaticAnalysisControlMode,
)
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan
from Monopoly.LlmEvaluation.Domain.Service.FallbackEligibilityChecker import FallbackEligibilityChecker
from Monopoly.LlmEvaluation.Domain.Service.SuppliedEvidenceValidator import SuppliedEvidenceValidator


class StaticAnalysisModeResolver:
    def __init__(
        self,
        *,
        evidenceValidator: SuppliedEvidenceValidator,
        fallbackChecker: FallbackEligibilityChecker,
    ) -> None:
        self._evidenceValidator = evidenceValidator
        self._fallbackChecker = fallbackChecker

    def resolve(self, judgeInput: JudgeInput) -> ResolvedRuntimePlan:
        requestedMode = judgeInput.resolvedControlMode()
        fallbackAuthorized = judgeInput.resolvedFallbackAllowed()
        algoId, algoVersion = judgeInput.requiredAlgorithm()
        dependencies = judgeInput.requiredDependencies()

        if requestedMode == StaticAnalysisControlMode.DISABLE_STATIC_ANALYSIS:
            return ResolvedRuntimePlan(
                requestedMode=requestedMode,
                executionMode=RuntimeExecutionMode.NO_STATIC_ANALYSIS,
                evidenceSource=None,
                algorithmId=None,
                algorithmVersion=None,
                dependencyVersions={},
                expectedExecutionStatus=ExecutionStatus.NOT_REQUESTED,
                fallbackAuthorized=False,
                fallbackRequired=False,
                fallbackAttempted=False,
                evidenceUsability=(),
                limitations=("Static analysis disabled by control mode.",),
                bundleRequired=False,
            )

        usabilityResults = self._evidenceValidator.classifyAll(judgeInput, algoId, algoVersion)
        best = SuppliedEvidenceValidator.bestUsability(usabilityResults)

        if best in (EvidenceUsability.USABLE, EvidenceUsability.PARTIALLY_USABLE):
            source = EvidenceSource.SUPPLIED_STATIC_SOFTWARE
            status = ExecutionStatus.COMPLETE if best == EvidenceUsability.USABLE else ExecutionStatus.PARTIAL
            depVersions = {depId: depVer for depId, depVer in dependencies}
            return ResolvedRuntimePlan(
                requestedMode=requestedMode,
                executionMode=RuntimeExecutionMode.STATIC_EVIDENCE_PROVIDED,
                evidenceSource=source,
                algorithmId=algoId,
                algorithmVersion=algoVersion,
                dependencyVersions=depVersions,
                expectedExecutionStatus=status,
                fallbackAuthorized=fallbackAuthorized,
                fallbackRequired=False,
                fallbackAttempted=False,
                evidenceUsability=usabilityResults,
                limitations=self._partialLimitations(usabilityResults),
                bundleRequired=False,
            )

        if requestedMode == StaticAnalysisControlMode.REQUIRE_PROVIDED_EVIDENCE:
            return self._noStaticAnalysis(
                requestedMode,
                fallbackAuthorized,
                usabilityResults,
                ("require_provided_evidence mode with no usable supplied evidence.",),
            )

        fallbackPermitted = fallbackAuthorized or requestedMode == StaticAnalysisControlMode.ALLOW_LLM_FALLBACK
        if not fallbackPermitted:
            return self._noStaticAnalysis(
                requestedMode,
                fallbackAuthorized,
                usabilityResults,
                ("No usable supplied evidence and fallback not authorized.",),
            )

        if not self._fallbackChecker.canVerify(algoId, algoVersion, dependencies):
            return self._noStaticAnalysis(
                requestedMode,
                fallbackAuthorized,
                usabilityResults,
                ("Fallback authorized but specification dependencies could not be verified.",),
            )

        depVersions = {depId: depVer for depId, depVer in dependencies}
        return ResolvedRuntimePlan(
            requestedMode=requestedMode,
            executionMode=RuntimeExecutionMode.LLM_STATIC_FALLBACK,
            evidenceSource=EvidenceSource.LLM_FALLBACK_GENERATED,
            algorithmId=algoId,
            algorithmVersion=algoVersion,
            dependencyVersions=depVersions,
            expectedExecutionStatus=ExecutionStatus.COMPLETE,
            fallbackAuthorized=True,
            fallbackRequired=True,
            fallbackAttempted=True,
            evidenceUsability=usabilityResults,
            limitations=(),
            bundleRequired=True,
        )

    def _noStaticAnalysis(
        self,
        requestedMode: str,
        fallbackAuthorized: bool,
        usabilityResults: tuple,
        limitations: tuple[str, ...],
    ) -> ResolvedRuntimePlan:
        return ResolvedRuntimePlan(
            requestedMode=requestedMode,
            executionMode=RuntimeExecutionMode.NO_STATIC_ANALYSIS,
            evidenceSource=None,
            algorithmId=None,
            algorithmVersion=None,
            dependencyVersions={},
            expectedExecutionStatus=ExecutionStatus.UNAVAILABLE,
            fallbackAuthorized=fallbackAuthorized,
            fallbackRequired=False,
            fallbackAttempted=False,
            evidenceUsability=usabilityResults,
            limitations=limitations,
            bundleRequired=False,
        )

    def _partialLimitations(self, usabilityResults: tuple) -> tuple[str, ...]:
        partial = [r.evidenceId for r in usabilityResults if r.usability == EvidenceUsability.PARTIALLY_USABLE]
        if not partial:
            return ()
        return (f"Partially usable supplied evidence: {', '.join(partial)}",)
