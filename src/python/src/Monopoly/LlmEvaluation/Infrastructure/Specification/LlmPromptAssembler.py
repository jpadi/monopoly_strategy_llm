"""Assemble the full LLM prompt from instruction paths, task prompt, and attachments."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmRequest
from Monopoly.LlmEvaluation.Domain.Port.SpecificationRepository import SpecificationRepository
from Monopoly.LlmEvaluation.Domain.Service.SpecificationAttachmentFormatter import (
    SpecificationAttachmentFormatter,
)

INSTRUCTIONS_SEPARATOR = "\n\n---\n\n"


class LlmPromptAssembler:
    def __init__(
        self,
        *,
        specificationRepository: SpecificationRepository,
        attachmentFormatter: SpecificationAttachmentFormatter | None = None,
    ) -> None:
        self._specificationRepository = specificationRepository
        self._attachmentFormatter = attachmentFormatter or SpecificationAttachmentFormatter()

    def assemble(self, request: LlmRequest) -> str:
        sections: list[str] = []
        if request.instructionFilePaths:
            instructionParts = [
                self._specificationRepository.readFile(path).decode("utf-8").strip()
                for path in request.instructionFilePaths
            ]
            sections.append(INSTRUCTIONS_SEPARATOR.join(instructionParts))
        if request.taskPrompt:
            sections.append(request.taskPrompt)
        if request.specificationBundle is not None and request.attachmentFilePaths:
            attached = self._attachmentFormatter.formatForPrompt(
                request.specificationBundle,
                attachmentFilePaths=request.attachmentFilePaths,
            )
            if attached:
                sections.append(attached)
        return "\n\n".join(section for section in sections if section)
