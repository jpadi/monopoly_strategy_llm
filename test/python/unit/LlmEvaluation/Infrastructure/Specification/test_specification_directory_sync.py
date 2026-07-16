"""Directory-to-bundle synchronization tests."""

from __future__ import annotations

from test_utilities.repo_paths import REPO_ROOT

from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    DELIVERABLE_SPEC_SUFFIX,
    LLM_EVALUATOR_DIR,
    STATIC_EVALUATOR_DIR,
    FileSystemSpecificationRepository,
)


def test_llm_evaluator_bundle_matches_directory():
    repository = FileSystemSpecificationRepository(docsRoot=REPO_ROOT)
    discovered = set(repository.llmEvaluatorBundlePaths())
    onDisk = set(
        f"{LLM_EVALUATOR_DIR}/{path.name}"
        for path in (REPO_ROOT / LLM_EVALUATOR_DIR).iterdir()
        if path.is_file() and path.name.endswith(DELIVERABLE_SPEC_SUFFIX)
    )
    assert discovered == onDisk
    assert len(discovered) >= 8
    assert "docs/llm_evaluator/02_input_specification.md" in discovered


def test_static_evaluator_bundle_matches_directory():
    repository = FileSystemSpecificationRepository(docsRoot=REPO_ROOT)
    discovered = set(repository.staticEvaluatorBundlePaths())
    onDisk = set(
        f"{STATIC_EVALUATOR_DIR}/{path.name}"
        for path in (REPO_ROOT / STATIC_EVALUATOR_DIR).iterdir()
        if path.is_file() and path.name.endswith(DELIVERABLE_SPEC_SUFFIX)
    )
    assert discovered == onDisk
    assert len(discovered) >= 2


def test_minimal_and_fallback_bundles_are_deterministic():
    repository = FileSystemSpecificationRepository(docsRoot=REPO_ROOT)
    minimal = repository.minimalBundlePaths()
    fallback = repository.fallbackBundlePaths()
    assert minimal == repository.llmEvaluatorBundlePaths()
    assert fallback == repository.llmEvaluatorBundlePaths() + repository.staticEvaluatorBundlePaths()
    assert len(minimal) == len(set(minimal))
    assert len(fallback) == len(set(fallback))
