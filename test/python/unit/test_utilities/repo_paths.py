"""Shared repository and fixture paths for tests."""

from __future__ import annotations

from Monopoly.bootstrap import repoRoot

REPO_ROOT = repoRoot()
FIXTURE_ROOT = REPO_ROOT / "test" / "python" / "fixtures" / "llm_evaluation"

INPUT_SPECIFICATION_PATH = "docs/llm_evaluator/02_input_specification.md"
