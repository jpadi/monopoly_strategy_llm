"""Architecture guard: LlmEvaluation module isolation."""

from __future__ import annotations

import ast
from pathlib import Path

from Monopoly.bootstrap import repoRoot


def _imports_in_package(package_root: Path) -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []
    for path in package_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    violations.append((str(path.relative_to(package_root)), alias.name))
            elif isinstance(node, ast.ImportFrom) and node.module:
                violations.append((str(path.relative_to(package_root)), node.module))
    return violations


def test_llm_evaluation_does_not_import_static_evaluation_domain():
    root = repoRoot() / "src/python/src/Monopoly/LlmEvaluation"
    forbidden = ("Monopoly.StaticEvaluation.Domain", "Monopoly.StaticEvaluation.Application")
    for filePath, module in _imports_in_package(root):
        assert not any(module.startswith(prefix) for prefix in forbidden), f"{filePath} imports {module}"


def test_domain_application_do_not_import_cursor_infrastructure():
    root = repoRoot() / "src/python/src/Monopoly/LlmEvaluation"
    for layer in ("Domain", "Application"):
        layer_root = root / layer
        if not layer_root.exists():
            continue
        for filePath, module in _imports_in_package(layer_root):
            assert "Infrastructure.Cursor" not in module, f"{filePath} imports {module}"


def test_domain_application_do_not_import_infrastructure():
    root = repoRoot() / "src/python/src/Monopoly/LlmEvaluation"
    for layer in ("Domain", "Application"):
        layer_root = root / layer
        if not layer_root.exists():
            continue
        for filePath, module in _imports_in_package(layer_root):
            assert not module.startswith("Monopoly.LlmEvaluation.Infrastructure"), f"{filePath} imports {module}"
