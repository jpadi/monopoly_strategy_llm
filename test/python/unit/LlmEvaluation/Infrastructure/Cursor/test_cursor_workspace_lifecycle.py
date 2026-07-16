"""Unit tests for Cursor execution workspace lifecycle."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from Monopoly.LlmEvaluation.Domain.Port.LlmClient import LlmRequest
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorExecutionWorkspace import CursorExecutionWorkspace
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorLlmClient import CursorLlmClient
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportError import CursorTransportError
from Monopoly.LlmEvaluation.Infrastructure.Specification.FileSystemSpecificationRepository import (
    FileSystemSpecificationRepository,
)
from test_utilities.judge_output_builder import buildCanonicalJudgeOutput
from test_utilities.repo_paths import REPO_ROOT


def _inlineEnvelope(content: dict) -> str:
    return json.dumps(
        {
            "transport_version": "1.0",
            "response_type": "inline_json",
            "content": content,
        }
    )


def _fileEnvelope(path: str) -> str:
    return json.dumps(
        {
            "transport_version": "1.0",
            "response_type": "file_reference",
            "file_reference": {
                "path": path,
                "format": "json",
                "encoding": "utf-8",
                "content_type": "application/json",
            },
        }
    )


@pytest.fixture
def specification_repository() -> FileSystemSpecificationRepository:
    return FileSystemSpecificationRepository(docsRoot=REPO_ROOT)


def test_workspace_create_without_subpath_uses_temporary_directory(monkeypatch):
    monkeypatch.delenv("MONOPOLY_ARTIFACT_SUBPATH", raising=False)
    workspace = CursorExecutionWorkspace.create()
    assert workspace.root.is_dir()
    assert workspace._temporaryDirectory is not None
    workspace.cleanup()
    assert not workspace.root.exists()


def test_workspace_create_with_subpath_persists_under_artifact(monkeypatch, tmp_path, llm_evaluation_artifact_subpath):
    if llm_evaluation_artifact_subpath is None:
        pytest.skip("Requires LlmEvaluation artifact subpath fixture")
    first = CursorExecutionWorkspace.create()
    second = CursorExecutionWorkspace.create()
    assert first.root != second.root
    assert first.root.is_dir()
    assert second.root.is_dir()
    assert "cursor_workspace" in str(first.root)
    first.cleanup()
    second.cleanup()
    assert first.root.is_dir()
    assert second.root.is_dir()


def test_each_complete_call_creates_unique_workspace(specification_repository, monkeypatch):
    monkeypatch.delenv("MONOPOLY_ARTIFACT_SUBPATH", raising=False)
    judgeOutput = buildCanonicalJudgeOutput()
    workspaces: list[str] = []

    class FakeResult:
        def __init__(self, text: str) -> None:
            self.result = text

    class FakeAgent:
        def __init__(self, options) -> None:
            workspaces.append(options["local"]["cwd"])

        def send(self, prompt):
            return self

        def wait(self):
            return FakeResult(_inlineEnvelope(judgeOutput))

        def close(self):
            return None

        def list_artifacts(self):
            return []

    fakeAgentModule = MagicMock()
    fakeAgentModule.Agent.create.side_effect = lambda options: FakeAgent(options)
    fakeAgentModule.AgentOptions = MagicMock(side_effect=lambda **kwargs: kwargs)

    client = CursorLlmClient(apiKey="test-key", specificationRepository=specification_repository)
    request = LlmRequest(
        model="fake-model",
        instructionFilePaths=[],
        attachmentFilePaths=[],
        taskPrompt="task",
        specificationBundle={},
    )

    with patch.dict("sys.modules", {"cursor_sdk": fakeAgentModule}):
        client.complete(request)
        client.complete(request)

    assert len(workspaces) == 2
    assert workspaces[0] != workspaces[1]
    assert not Path(workspaces[0]).exists()
    assert not Path(workspaces[1]).exists()


def test_cleanup_after_inline_response(specification_repository, monkeypatch):
    monkeypatch.delenv("MONOPOLY_ARTIFACT_SUBPATH", raising=False)
    judgeOutput = buildCanonicalJudgeOutput()
    capturedWorkspace: list[Path] = []

    class FakeResult:
        result = _inlineEnvelope(judgeOutput)

    class FakeAgent:
        def __init__(self, options) -> None:
            capturedWorkspace.append(Path(options["local"]["cwd"]))

        def send(self, prompt):
            return self

        def wait(self):
            return FakeResult()

        def close(self):
            return None

        def list_artifacts(self):
            return []

    fakeAgentModule = MagicMock()
    fakeAgentModule.Agent.create.side_effect = lambda options: FakeAgent(options)
    fakeAgentModule.AgentOptions = MagicMock(side_effect=lambda **kwargs: kwargs)

    client = CursorLlmClient(apiKey="test-key", specificationRepository=specification_repository)
    request = LlmRequest(
        model="fake-model",
        instructionFilePaths=[],
        attachmentFilePaths=[],
        taskPrompt="task",
        specificationBundle={},
    )

    with patch.dict("sys.modules", {"cursor_sdk": fakeAgentModule}):
        client.complete(request)

    assert capturedWorkspace
    assert not capturedWorkspace[0].exists()


def test_cleanup_after_file_reference_response(specification_repository, monkeypatch):
    monkeypatch.delenv("MONOPOLY_ARTIFACT_SUBPATH", raising=False)
    judgeOutput = buildCanonicalJudgeOutput()
    capturedWorkspace: list[Path] = []

    class FakeResult:
        result = _fileEnvelope("output/judge_output.json")

    class FakeAgent:
        def __init__(self, options) -> None:
            root = Path(options["local"]["cwd"])
            capturedWorkspace.append(root)
            target = root / "output" / "judge_output.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(judgeOutput), encoding="utf-8")

        def send(self, prompt):
            return self

        def wait(self):
            return FakeResult()

        def close(self):
            return None

        def list_artifacts(self):
            return []

    fakeAgentModule = MagicMock()
    fakeAgentModule.Agent.create.side_effect = lambda options: FakeAgent(options)
    fakeAgentModule.AgentOptions = MagicMock(side_effect=lambda **kwargs: kwargs)

    client = CursorLlmClient(apiKey="test-key", specificationRepository=specification_repository)
    request = LlmRequest(
        model="fake-model",
        instructionFilePaths=[],
        attachmentFilePaths=[],
        taskPrompt="task",
        specificationBundle={},
    )

    with patch.dict("sys.modules", {"cursor_sdk": fakeAgentModule}):
        response = client.complete(request)

    assert json.loads(response.rawText) == judgeOutput
    assert capturedWorkspace
    assert not capturedWorkspace[0].exists()


def test_cleanup_after_transport_envelope_failure(specification_repository, monkeypatch):
    monkeypatch.delenv("MONOPOLY_ARTIFACT_SUBPATH", raising=False)
    capturedWorkspace: list[Path] = []

    class FakeResult:
        result = "unstructured prose only"

    class FakeAgent:
        def __init__(self, options) -> None:
            capturedWorkspace.append(Path(options["local"]["cwd"]))

        def send(self, prompt):
            return self

        def wait(self):
            return FakeResult()

        def close(self):
            return None

        def list_artifacts(self):
            return []

    fakeAgentModule = MagicMock()
    fakeAgentModule.Agent.create.side_effect = lambda options: FakeAgent(options)
    fakeAgentModule.AgentOptions = MagicMock(side_effect=lambda **kwargs: kwargs)

    client = CursorLlmClient(apiKey="test-key", specificationRepository=specification_repository)
    request = LlmRequest(
        model="fake-model",
        instructionFilePaths=[],
        attachmentFilePaths=[],
        taskPrompt="task",
        specificationBundle={},
    )

    with patch.dict("sys.modules", {"cursor_sdk": fakeAgentModule}):
        with pytest.raises(CursorTransportError):
            client.complete(request)

    assert capturedWorkspace
    assert not capturedWorkspace[0].exists()


def test_cleanup_after_file_retrieval_failure(specification_repository, monkeypatch):
    monkeypatch.delenv("MONOPOLY_ARTIFACT_SUBPATH", raising=False)
    capturedWorkspace: list[Path] = []

    class FakeResult:
        result = _fileEnvelope("missing/output.json")

    class FakeAgent:
        def __init__(self, options) -> None:
            capturedWorkspace.append(Path(options["local"]["cwd"]))

        def send(self, prompt):
            return self

        def wait(self):
            return FakeResult()

        def close(self):
            return None

        def list_artifacts(self):
            return []

    fakeAgentModule = MagicMock()
    fakeAgentModule.Agent.create.side_effect = lambda options: FakeAgent(options)
    fakeAgentModule.AgentOptions = MagicMock(side_effect=lambda **kwargs: kwargs)

    client = CursorLlmClient(apiKey="test-key", specificationRepository=specification_repository)
    request = LlmRequest(
        model="fake-model",
        instructionFilePaths=[],
        attachmentFilePaths=[],
        taskPrompt="task",
        specificationBundle={},
    )

    with patch.dict("sys.modules", {"cursor_sdk": fakeAgentModule}):
        with pytest.raises(CursorTransportError):
            client.complete(request)

    assert capturedWorkspace
    assert not capturedWorkspace[0].exists()


def test_artifact_subpath_workspace_preserved_after_cleanup(llm_evaluation_artifact_subpath):
    if llm_evaluation_artifact_subpath is None:
        pytest.skip("Requires LlmEvaluation artifact subpath fixture")
    workspace = CursorExecutionWorkspace.create()
    marker = workspace.root / "marker.txt"
    marker.write_text("keep", encoding="utf-8")
    workspace.cleanup()
    assert workspace.root.is_dir()
    assert marker.is_file()
