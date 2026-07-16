import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from Monopoly.Shared.Infrastructure.ArtifactStore import (
    artifactRelativePathFromPytestNode,
    clearArtifactDirectory,
    ensureArtifactDirectory,
    writeArtifactJson,
)
from Monopoly.Shared.Infrastructure.EnvironmentLoader import loadRepositoryEnvironment

loadRepositoryEnvironment()


@pytest.fixture(scope="session", autouse=True)
def bootstrap_artifact_directory():
    """Clear artifact/ once per test session so runs do not accumulate stale output."""
    if os.environ.get("MONOPOLY_KEEP_ARTIFACTS", "").strip():
        yield
        return
    clearArtifactDirectory()
    yield


@pytest.fixture(autouse=True)
def llm_evaluation_artifact_subpath(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    """Mirror pytest node path under artifact/ for every LlmEvaluation test."""
    nodePath = str(getattr(request.node, "fspath", "")).replace("\\", "/")
    if "/LlmEvaluation/" not in nodePath:
        yield None
        return

    relative = artifactRelativePathFromPytestNode(request.node.nodeid)
    monkeypatch.setenv("MONOPOLY_ARTIFACT_SUBPATH", relative)
    target = ensureArtifactDirectory(*relative.split("/"))
    writeArtifactJson(
        f"{relative}/manifest.json",
        {
            "nodeid": request.node.nodeid,
            "artifact_path": relative,
        },
    )
    yield target
    monkeypatch.delenv("MONOPOLY_ARTIFACT_SUBPATH", raising=False)
