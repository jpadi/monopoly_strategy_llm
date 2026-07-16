"""Unit tests for SpecificationAttachmentFormatter."""

from __future__ import annotations

from Monopoly.LlmEvaluation.Domain.Model.Specification.SpecificationBundle import (
    BundleFile,
    SpecificationBundle,
    SpecificationStructureManifest,
)
from Monopoly.LlmEvaluation.Domain.Service.SpecificationAttachmentFormatter import (
    SpecificationAttachmentFormatter,
)


def test_format_for_prompt_includes_only_requested_paths():
    bundle = SpecificationBundle(
        files=(
            BundleFile(
                relativePath="docs/llm_evaluator/00_initial_prompt.md",
                content=b"# Initial",
            ),
            BundleFile(
                relativePath="docs/llm_evaluator/01_judge.md",
                content=b"# Judge spec",
            ),
        ),
        structureManifest=SpecificationStructureManifest(
            rootLabel="docs",
            treeText="docs/",
            readOrder=("docs/llm_evaluator/01_judge.md",),
            linkNotes=(),
        ),
    )

    formatted = SpecificationAttachmentFormatter().formatForPrompt(
        bundle,
        attachmentFilePaths=("docs/llm_evaluator/01_judge.md",),
    )

    assert "--- BEGIN ATTACHED FILE: docs/llm_evaluator/01_judge.md ---" in formatted
    assert "# Judge spec" in formatted
    assert "00_initial_prompt.md" not in formatted


def test_format_for_prompt_returns_empty_when_no_paths():
    bundle = SpecificationBundle(
        files=(
            BundleFile(
                relativePath="docs/llm_evaluator/00_initial_prompt.md",
                content=b"# Initial",
            ),
        ),
        structureManifest=SpecificationStructureManifest(
            rootLabel="docs",
            treeText="docs/",
            readOrder=("docs/llm_evaluator/00_initial_prompt.md",),
            linkNotes=(),
        ),
    )

    formatted = SpecificationAttachmentFormatter().formatForPrompt(
        bundle,
        attachmentFilePaths=(),
    )

    assert formatted == ""
