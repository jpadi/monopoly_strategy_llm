"""Provider-neutral specification file bundle."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BundleFile:
    relativePath: str
    content: bytes


@dataclass(frozen=True, slots=True)
class SpecificationStructureManifest:
    rootLabel: str
    treeText: str
    readOrder: tuple[str, ...]
    linkNotes: tuple[str, ...]
    instructionFilePaths: tuple[str, ...] = ()
    attachmentFilePaths: tuple[str, ...] = ()
    deliveredFilePaths: tuple[str, ...] = ()

    def formatForPrompt(self) -> str:
        lines = [
            "## Specification delivery manifest",
            "Authoritative list of every file delivered for this request.",
            "",
            f"Instruction files ({len(self.instructionFilePaths)}):",
            *[f"- {path}" for path in self.instructionFilePaths],
            "",
            f"Attachment files ({len(self.attachmentFilePaths)}):",
            *[f"- {path}" for path in self.attachmentFilePaths],
            "",
            f"Delivered files ({len(self.deliveredFilePaths)}):",
            *[f"- {path}" for path in self.deliveredFilePaths],
            "",
            "Directory tree:",
            self.treeText,
            "",
            f"Specification read order: {' → '.join(self.readOrder)}",
        ]
        if self.linkNotes:
            lines.append("")
            lines.extend(self.linkNotes)
        lines.append("Compare attachment headers in the message with this manifest to confirm completeness.")
        return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class SpecificationBundle:
    files: tuple[BundleFile, ...]
    structureManifest: SpecificationStructureManifest
