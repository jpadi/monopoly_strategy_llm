"""Architecture guards for Cursor transport isolation."""

from __future__ import annotations

import ast
from pathlib import Path

from Monopoly.bootstrap import repoRoot


def _file_contains_terms(path: Path, forbidden_terms: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8").lower()
    return [term for term in forbidden_terms if term.lower() in text]


def test_judge_specs_do_not_reference_cursor_transport():
    root = repoRoot() / "docs/llm_evaluator"
    forbidden = (
        "cursor sdk",
        "sidecar",
        "file_reference transport",
        "transport envelope",
        "judge_output_response.json",
        "judge_final.json",
        "/tmp/judge_final.json",
    )
    violations: list[str] = []
    for path in root.rglob("*.md"):
        matches = _file_contains_terms(path, forbidden)
        if matches:
            violations.append(f"{path.relative_to(repoRoot())}: {matches}")
    assert not violations, "\n".join(violations)


def test_static_evaluator_specs_do_not_reference_cursor_transport():
    root = repoRoot() / "docs/static_evaluator"
    forbidden = ("sidecar", "transport envelope", "file_reference transport", "judge_output_response.json")
    violations: list[str] = []
    for path in root.rglob("*.md"):
        matches = _file_contains_terms(path, forbidden)
        if matches:
            violations.append(f"{path.relative_to(repoRoot())}: {matches}")
    assert not violations, "\n".join(violations)


def test_judge_response_parser_does_not_access_filesystem():
    parserPath = (
        repoRoot()
        / "src/python/src/Monopoly/LlmEvaluation/Domain/Service/JudgeResponseParser.py"
    )
    tree = ast.parse(parserPath.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in {"pathlib", "os", "open"}, (
                    "JudgeResponseParser must not import filesystem modules"
                )
        if isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] not in {"pathlib", "os"}, (
                "JudgeResponseParser must not import filesystem modules"
            )
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open", "JudgeResponseParser must not open files"
