"""Format specification bundle files for API prompt delivery."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Model.Specification.SpecificationAttachmentEnvelope import (
    SpecificationAttachmentEnvelope,
)
from Monopoly.LlmEvaluation.Domain.Model.Specification.SpecificationBundle import SpecificationBundle


class SpecificationAttachmentFormatter:
    def formatForPrompt(
        self,
        bundle: SpecificationBundle,
        *,
        attachmentFilePaths: tuple[str, ...],
    ) -> str:
        if not attachmentFilePaths:
            return ""

        filesByPath = {bundleFile.relativePath: bundleFile for bundleFile in bundle.files}
        sections = [SpecificationAttachmentEnvelope.ATTACHED_FILES_HEADING]
        attached = False
        for relativePath in attachmentFilePaths:
            bundleFile = filesByPath.get(relativePath)
            if bundleFile is None:
                continue
            attached = True
            text = bundleFile.content.decode("utf-8")
            sections.extend(
                [
                    "",
                    SpecificationAttachmentEnvelope.beginMarker(relativePath),
                    text,
                    SpecificationAttachmentEnvelope.endMarker(relativePath),
                ]
            )
        if not attached:
            return ""
        return "\n".join(sections)
