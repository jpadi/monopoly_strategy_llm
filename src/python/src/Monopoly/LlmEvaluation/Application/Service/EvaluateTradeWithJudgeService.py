"""Orchestrate Judge evaluation with pre-LLM resolution and one repair attempt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import (
    JudgeOutputParseError,
    JudgeOutputSchemaViolationError,
    JudgeRepairFailureError,
)
from Monopoly.LlmEvaluation.Domain.Model.Artifact.JudgeExecutionArtifactTrace import JudgeExecutionArtifactTrace
from Monopoly.LlmEvaluation.Domain.Model.Input.JudgeInputValidator import validateJudgeInput
from Monopoly.LlmEvaluation.Domain.Model.JudgeValidationError import JudgeValidationErrorRecord
from Monopoly.LlmEvaluation.Domain.Model.Output.JudgeOutput import JudgeOutput
from Monopoly.LlmEvaluation.Domain.Model.Request.JudgeEvaluationRequest import JudgeEvaluationRequest
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan
from Monopoly.LlmEvaluation.Domain.Model.Specification.SpecificationBundle import SpecificationBundle
from Monopoly.LlmEvaluation.Domain.Port.JudgeArtifactRecorder import JudgeArtifactRecorder
from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmClient, LlmRequest, LlmResponse
from Monopoly.LlmEvaluation.Domain.Service.FallbackEligibilityChecker import FallbackEligibilityChecker
from Monopoly.LlmEvaluation.Domain.Service.JudgeOutputValidator import JudgeOutputValidator
from Monopoly.LlmEvaluation.Domain.Service.JudgePromptBuilder import JudgePromptBuilder
from Monopoly.LlmEvaluation.Domain.Service.JudgeResponseParser import JudgeResponseParser
from Monopoly.LlmEvaluation.Domain.Service.JudgeValidationErrorFactory import outputParseError
from Monopoly.LlmEvaluation.Domain.Service.SpecificationBundleBuilder import SpecificationBundleBuilder
from Monopoly.LlmEvaluation.Domain.Service.StaticAnalysisModeResolver import StaticAnalysisModeResolver
from Monopoly.LlmEvaluation.Domain.Service.SuppliedEvidenceValidator import SuppliedEvidenceValidator


@dataclass(frozen=True, slots=True)
class JudgeExecutionMetadata:
    repairAttempted: bool
    repairCount: int
    originalValidationErrors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class JudgeEvaluationResult:
    output: JudgeOutput
    metadata: JudgeExecutionMetadata


@dataclass(frozen=True, slots=True)
class _InitialFailureContext:
    errors: tuple[str, ...]
    structuredErrors: tuple[JudgeValidationErrorRecord, ...]
    invalidOutput: dict[str, Any] | None
    invalidRawText: str | None
    parseError: str | None


class EvaluateTradeWithJudgeService:
    def __init__(
        self,
        *,
        llmClient: LlmClient,
        modeResolver: StaticAnalysisModeResolver,
        bundleBuilder: SpecificationBundleBuilder,
        promptBuilder: JudgePromptBuilder,
        responseParser: JudgeResponseParser,
        outputValidator: JudgeOutputValidator,
        artifactRecorder: JudgeArtifactRecorder,
    ) -> None:
        self._llmClient = llmClient
        self._modeResolver = modeResolver
        self._bundleBuilder = bundleBuilder
        self._promptBuilder = promptBuilder
        self._responseParser = responseParser
        self._outputValidator = outputValidator
        self._artifactRecorder = artifactRecorder

    def execute(self, request: JudgeEvaluationRequest) -> JudgeEvaluationResult:
        request.llmExecution.validate()
        validateJudgeInput(request.evaluationInput)

        runtimePlan = self._modeResolver.resolve(request.evaluationInput)
        bundle = self._bundleBuilder.build(runtimePlan)

        llmRequest = self._promptBuilder.build(
            request.evaluationInput,
            runtimePlan,
            bundle,
            model=request.llmExecution.model,
            timeoutSeconds=request.llmExecution.timeoutSeconds,
        )
        initialResponse = self._llmClient.complete(llmRequest)

        trace = JudgeExecutionArtifactTrace(
            initialRequest=llmRequest,
            initialResponse=initialResponse,
        )
        repairAttempted = False
        repairCount = 0
        originalErrors: tuple[str, ...] = ()
        outputDict: dict[str, Any] | None = None
        output: JudgeOutput | None = None
        failureContext: _InitialFailureContext | None = None

        try:
            try:
                outputDict = self._responseParser.parse(initialResponse.rawText)
                trace = JudgeExecutionArtifactTrace(
                    initialRequest=llmRequest,
                    initialResponse=initialResponse,
                    initialOutputDict=outputDict,
                )
                output = self._outputValidator.validate(outputDict, runtimePlan)
            except JudgeOutputParseError as parseError:
                failureContext = _InitialFailureContext(
                    errors=(str(parseError),),
                    structuredErrors=(outputParseError(message=str(parseError)),),
                    invalidOutput=None,
                    invalidRawText=initialResponse.rawText,
                    parseError=str(parseError),
                )
                trace = JudgeExecutionArtifactTrace(
                    initialRequest=llmRequest,
                    initialResponse=initialResponse,
                    initialParseError=str(parseError),
                    initialValidationErrors=(str(parseError),),
                    initialStructuredErrors=(outputParseError(message=str(parseError)),),
                )
            except JudgeOutputSchemaViolationError as validationError:
                failureContext = _InitialFailureContext(
                    errors=validationError.errors,
                    structuredErrors=validationError.structuredErrors,
                    invalidOutput=outputDict,
                    invalidRawText=None,
                    parseError=None,
                )
                trace = JudgeExecutionArtifactTrace(
                    initialRequest=llmRequest,
                    initialResponse=initialResponse,
                    initialOutputDict=outputDict,
                    initialValidationErrors=validationError.errors,
                    initialStructuredErrors=validationError.structuredErrors,
                )

            if failureContext is not None:
                if bundle is None:
                    raise RuntimeError("Specification bundle is required for Judge repair")
                originalErrors = failureContext.errors
                repairAttempted = True
                repairCount = 1
                try:
                    output, outputDict, trace = self._attemptRepair(
                        request=request,
                        runtimePlan=runtimePlan,
                        bundle=bundle,
                        llmRequest=llmRequest,
                        initialResponse=initialResponse,
                        failureContext=failureContext,
                        outputDict=outputDict,
                        trace=trace,
                    )
                except JudgeRepairFailureError as repairFailure:
                    if repairFailure.artifactTrace is not None:
                        trace = repairFailure.artifactTrace
                    raise
        finally:
            self._artifactRecorder.recordExecution(
                request=request,
                runtimePlan=runtimePlan,
                trace=trace,
                finalOutputDict=outputDict if output is not None else None,
                provider=request.llmExecution.provider,
            )

        assert output is not None
        return JudgeEvaluationResult(
            output=output,
            metadata=JudgeExecutionMetadata(
                repairAttempted=repairAttempted,
                repairCount=repairCount,
                originalValidationErrors=originalErrors,
            ),
        )

    def _attemptRepair(
        self,
        *,
        request: JudgeEvaluationRequest,
        runtimePlan: ResolvedRuntimePlan,
        bundle: SpecificationBundle,
        llmRequest: LlmRequest,
        initialResponse: LlmResponse,
        failureContext: _InitialFailureContext,
        outputDict: dict[str, Any] | None,
        trace: JudgeExecutionArtifactTrace,
    ) -> tuple[JudgeOutput, dict[str, Any], JudgeExecutionArtifactTrace]:
        repairRequest = self._promptBuilder.build(
            request.evaluationInput,
            runtimePlan,
            bundle,
            model=request.llmExecution.model,
            timeoutSeconds=request.llmExecution.timeoutSeconds,
            repairErrors=failureContext.errors,
            repairStructuredErrors=failureContext.structuredErrors,
            repairInvalidOutput=failureContext.invalidOutput,
            repairInvalidRawText=failureContext.invalidRawText,
        )
        repairResponse = self._llmClient.complete(repairRequest)
        repairOutputDict: dict[str, Any] | None = None
        trace = JudgeExecutionArtifactTrace(
            initialRequest=llmRequest,
            initialResponse=initialResponse,
            initialOutputDict=outputDict,
            initialParseError=failureContext.parseError,
            initialValidationErrors=failureContext.errors,
            initialStructuredErrors=failureContext.structuredErrors,
            repairAttempted=True,
            repairRequest=repairRequest,
            repairResponse=repairResponse,
        )
        try:
            repairOutputDict = self._responseParser.parse(repairResponse.rawText)
            output = self._outputValidator.validate(repairOutputDict, runtimePlan)
            trace = JudgeExecutionArtifactTrace(
                initialRequest=llmRequest,
                initialResponse=initialResponse,
                initialOutputDict=outputDict,
                initialParseError=failureContext.parseError,
                initialValidationErrors=failureContext.errors,
                initialStructuredErrors=failureContext.structuredErrors,
                repairAttempted=True,
                repairRequest=repairRequest,
                repairResponse=repairResponse,
                repairOutputDict=repairOutputDict,
            )
            return output, repairOutputDict, trace
        except JudgeOutputParseError as repairParseError:
            trace = JudgeExecutionArtifactTrace(
                initialRequest=llmRequest,
                initialResponse=initialResponse,
                initialOutputDict=outputDict,
                initialParseError=failureContext.parseError,
                initialValidationErrors=failureContext.errors,
                initialStructuredErrors=failureContext.structuredErrors,
                repairAttempted=True,
                repairRequest=repairRequest,
                repairResponse=repairResponse,
                repairParseError=str(repairParseError),
            )
            raise JudgeRepairFailureError(
                "Judge repair response could not be parsed as JSON",
                initialValidationErrors=failureContext.errors,
                initialStructuredErrors=failureContext.structuredErrors,
                repairParseError=str(repairParseError),
                artifactTrace=trace,
            ) from repairParseError
        except JudgeOutputSchemaViolationError as repairValidationError:
            trace = JudgeExecutionArtifactTrace(
                initialRequest=llmRequest,
                initialResponse=initialResponse,
                initialOutputDict=outputDict,
                initialParseError=failureContext.parseError,
                initialValidationErrors=failureContext.errors,
                initialStructuredErrors=failureContext.structuredErrors,
                repairAttempted=True,
                repairRequest=repairRequest,
                repairResponse=repairResponse,
                repairOutputDict=repairOutputDict,
                repairValidationErrors=repairValidationError.errors,
                repairStructuredErrors=repairValidationError.structuredErrors,
            )
            raise JudgeRepairFailureError(
                "Judge repair response failed schema validation",
                initialValidationErrors=failureContext.errors,
                initialStructuredErrors=failureContext.structuredErrors,
                repairValidationErrors=repairValidationError.errors,
                repairStructuredErrors=repairValidationError.structuredErrors,
                artifactTrace=trace,
            ) from repairValidationError


def createDefaultModeResolver(
    *,
    specificationRepository: Any,
) -> StaticAnalysisModeResolver:
    evidenceValidator = SuppliedEvidenceValidator()
    fallbackChecker = FallbackEligibilityChecker(specificationRepository=specificationRepository)
    return StaticAnalysisModeResolver(
        evidenceValidator=evidenceValidator,
        fallbackChecker=fallbackChecker,
    )
