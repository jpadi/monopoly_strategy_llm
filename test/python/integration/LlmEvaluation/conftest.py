"""Shared fixtures for LLM Judge integration tests."""

from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def cursor_api_key() -> str:
    import os

    key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not key:
        pytest.skip("CURSOR_API_KEY is not set (configure repository root .env or export the variable)")
    return key


@pytest.fixture(scope="session")
def cursor_judge_model() -> str:
    import os

    return os.environ.get("CURSOR_JUDGE_MODEL", "composer-2.5").strip() or "composer-2.5"


@pytest.fixture
def integration_artifact_dir(llm_evaluation_artifact_subpath):
    if llm_evaluation_artifact_subpath is None:
        pytest.skip("Not an LlmEvaluation test")
    return llm_evaluation_artifact_subpath
