"""Filesystem-backed specification repository."""

from __future__ import annotations

import re
from pathlib import Path

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import LlmEvaluationError

_ID_PATTERN = re.compile(
    r"specification_id\s*=\s*(\S+)\s*\n\s*specification_version\s*=\s*(\S+)",
    re.MULTILINE,
)

LLM_EVALUATOR_DIR = "docs/llm_evaluator"
STATIC_EVALUATOR_DIR = "docs/static_evaluator"
DELIVERABLE_SPEC_SUFFIX = ".md"


class FileSystemSpecificationRepository:
    def __init__(self, *, docsRoot: Path) -> None:
        self._docsRoot = docsRoot

    def readFile(self, relativePath: str) -> bytes:
        path = self._docsRoot / relativePath
        if not path.is_file():
            raise LlmEvaluationError(f"Specification file not found: {relativePath}")
        return path.read_bytes()

    def verifySpecificationIdentity(self, specificationId: str, requiredVersion: str) -> bool:
        path = self._resolveSpecPath(specificationId)
        if path is None or not path.is_file():
            return False
        content = path.read_text(encoding="utf-8")
        match = _ID_PATTERN.search(content)
        if not match:
            return False
        foundId, foundVersion = match.group(1), match.group(2)
        return foundId == specificationId and foundVersion == requiredVersion

    def discoverDeliverablePaths(self, relativeDirectory: str) -> tuple[str, ...]:
        directory = self._docsRoot / relativeDirectory
        if not directory.is_dir():
            return ()
        paths = sorted(
            f"{relativeDirectory}/{entry.name}"
            for entry in directory.iterdir()
            if entry.is_file() and entry.name.endswith(DELIVERABLE_SPEC_SUFFIX)
        )
        return tuple(paths)

    def llmEvaluatorBundlePaths(self) -> tuple[str, ...]:
        return self.discoverDeliverablePaths(LLM_EVALUATOR_DIR)

    def staticEvaluatorBundlePaths(self) -> tuple[str, ...]:
        return self.discoverDeliverablePaths(STATIC_EVALUATOR_DIR)

    def minimalBundlePaths(self) -> tuple[str, ...]:
        return self.llmEvaluatorBundlePaths()

    def fallbackBundlePaths(self) -> tuple[str, ...]:
        return self.llmEvaluatorBundlePaths() + self.staticEvaluatorBundlePaths()

    def defaultJudgeBundlePaths(self) -> tuple[str, ...]:
        return self.minimalBundlePaths()

    def _resolveSpecPath(self, specificationId: str) -> Path | None:
        mapping = {
            "monopoly_static_algorithm": self._docsRoot / "docs/static_evaluator/static_algorithm_specification.md",
            "monopoly_risk_reference": self._docsRoot / "docs/static_evaluator/risk_reference.md",
        }
        return mapping.get(specificationId)
