"""Infrastructure adapter for Judge execution artifact recording."""

from __future__ import annotations

from typing import Any

from Monopoly.LlmEvaluation.Domain.Model.Artifact.JudgeExecutionArtifactTrace import JudgeExecutionArtifactTrace
from Monopoly.LlmEvaluation.Domain.Model.Request.JudgeEvaluationRequest import JudgeEvaluationRequest
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan
from Monopoly.LlmEvaluation.Infrastructure.Artifact.JudgeArtifactWriter import JudgeArtifactWriter
from Monopoly.Shared.Infrastructure.ArtifactStore import currentArtifactSubpath


class DefaultJudgeArtifactRecorder:
    def recordExecution(
        self,
        *,
        request: JudgeEvaluationRequest,
        runtimePlan: ResolvedRuntimePlan,
        trace: JudgeExecutionArtifactTrace,
        finalOutputDict: dict[str, Any] | None = None,
        provider: str,
    ) -> None:
        if not currentArtifactSubpath() and provider.strip().lower() == "fake":
            return
        JudgeArtifactWriter.writeExecutionArtifacts(
            request=request,
            runtimePlan=runtimePlan,
            trace=trace,
            finalOutputDict=finalOutputDict,
        )


class NullJudgeArtifactRecorder:
    def recordExecution(
        self,
        *,
        request: JudgeEvaluationRequest,
        runtimePlan: ResolvedRuntimePlan,
        trace: JudgeExecutionArtifactTrace,
        finalOutputDict: dict[str, Any] | None = None,
        provider: str,
    ) -> None:
        return
