"""Port for recording Judge execution artifacts."""

from __future__ import annotations

from typing import Any, Protocol

from Monopoly.LlmEvaluation.Domain.Model.Artifact.JudgeExecutionArtifactTrace import JudgeExecutionArtifactTrace
from Monopoly.LlmEvaluation.Domain.Model.Request.JudgeEvaluationRequest import JudgeEvaluationRequest
from Monopoly.LlmEvaluation.Domain.Model.Runtime.ResolvedRuntimePlan import ResolvedRuntimePlan


class JudgeArtifactRecorder(Protocol):
    def recordExecution(
        self,
        *,
        request: JudgeEvaluationRequest,
        runtimePlan: ResolvedRuntimePlan,
        trace: JudgeExecutionArtifactTrace,
        finalOutputDict: dict[str, Any] | None = None,
        provider: str,
    ) -> None: ...
