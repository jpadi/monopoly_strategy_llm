"""Deterministic fake LLM client for unit and functional tests."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from test_utilities.repo_paths import INPUT_SPECIFICATION_PATH

from Monopoly.LlmEvaluation.Domain.Port.LlmClient import (
    LlmClient,
    LlmRequest,
    LlmResponse,
)
from Monopoly.LlmEvaluation.Domain.Service.JudgePromptBuilder import (
    FILE_ATTACHMENT_STANDARD_PATH,
    INITIAL_PROMPT_PATH,
)


@dataclass
class FakeLlmClient(LlmClient):
    responsesByScenario: dict[str, dict[str, Any]] = field(default_factory=dict)
    defaultResponse: dict[str, Any] | None = None
    calls: list[LlmRequest] = field(default_factory=list)
    activeScenarioId: str = "competitive_only"
    repairResponseText: str | None = None
    initialResponseText: str | None = None

    def complete(self, request: LlmRequest) -> LlmResponse:
        self.calls.append(request)
        if len(self.calls) == 1 and self.initialResponseText is not None:
            return LlmResponse(
                rawText=self.initialResponseText,
                modelUsed=request.model,
                finishReason="stop",
            )
        if len(self.calls) == 2 and self.repairResponseText is not None:
            return LlmResponse(
                rawText=self.repairResponseText,
                modelUsed=request.model,
                finishReason="stop",
            )
        payload = self.responsesByScenario.get(self.activeScenarioId, self.defaultResponse)
        if payload is None:
            raise RuntimeError(f"No fake LLM response configured for scenario {self.activeScenarioId}")
        return LlmResponse(
            rawText=json.dumps(payload),
            modelUsed=request.model,
            finishReason="stop",
        )

    @property
    def lastCall(self) -> LlmRequest | None:
        return self.calls[-1] if self.calls else None

    def requestIncludesInitialPromptPath(self) -> bool:
        if self.lastCall is None:
            return False
        return INITIAL_PROMPT_PATH in self.lastCall.instructionFilePaths

    def requestIncludesAttachmentStandardPath(self) -> bool:
        if self.lastCall is None:
            return False
        return FILE_ATTACHMENT_STANDARD_PATH in self.lastCall.instructionFilePaths

    def requestIncludesJudgeAttachmentPath(self) -> bool:
        if self.lastCall is None:
            return False
        return "docs/llm_evaluator/01_judge.md" in self.lastCall.attachmentFilePaths

    def requestIncludesInputSpecificationPath(self) -> bool:
        if self.lastCall is None:
            return False
        return INPUT_SPECIFICATION_PATH in self.lastCall.attachmentFilePaths

    def taskPromptOmitsSpecBodies(self) -> bool:
        if self.lastCall is None:
            return False
        markers = (
            "--- BEGIN ATTACHED FILE:",
            "# Monopoly Trade Evaluation Judge Specification",
            "Evidence envelope (exact field names)",
        )
        return not any(marker in self.lastCall.taskPrompt for marker in markers)

    def bundleIncludesInitialPrompt(self) -> bool:
        if self.lastCall is None or self.lastCall.specificationBundle is None:
            return False
        return any(file.relativePath == INITIAL_PROMPT_PATH for file in self.lastCall.specificationBundle.files)

    def manifestMatchesDeliveredPaths(self) -> bool:
        if self.lastCall is None or self.lastCall.specificationBundle is None:
            return False
        manifest = self.lastCall.specificationBundle.structureManifest
        expected = self.lastCall.instructionFilePaths + self.lastCall.attachmentFilePaths
        return manifest.deliveredFilePaths == expected
