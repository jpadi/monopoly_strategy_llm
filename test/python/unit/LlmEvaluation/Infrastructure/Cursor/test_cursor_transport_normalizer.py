"""Unit tests for Cursor transport envelope parsing and normalization."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorLegacyProseRecovery import CursorLegacyProseRecovery
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportEnvelopeParser import CursorTransportEnvelopeParser
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportError import CursorTransportError
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportNormalizer import CursorTransportNormalizer
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorWorkspacePathResolver import CursorWorkspacePathResolver
from test_utilities.judge_output_builder import buildCanonicalJudgeOutput


class _FakeAgent:
    def __init__(self, *, artifacts: dict[str, bytes] | None = None) -> None:
        self._artifacts = artifacts or {}

    def list_artifacts(self):
        return [
            type("Artifact", (), {"path": path, "size_bytes": len(content)})()
            for path, content in self._artifacts.items()
        ]

    def download_artifact(self, path: str) -> bytes:
        if path not in self._artifacts:
            raise RuntimeError(f"missing artifact {path}")
        return self._artifacts[path]


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    root = tmp_path / "workspace"
    root.mkdir()
    return root


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


def test_valid_inline_json_envelope(workspace: Path):
    judgeOutput = buildCanonicalJudgeOutput()
    normalized, diagnostics = CursorTransportNormalizer.normalize(
        rawProviderText=_inlineEnvelope(judgeOutput),
        workspaceRoot=workspace,
    )
    assert json.loads(normalized) == judgeOutput
    assert diagnostics.transportEnvelopeDetected is True
    assert diagnostics.responseType == "inline_json"


def test_valid_file_reference_envelope(workspace: Path):
    judgeOutput = buildCanonicalJudgeOutput()
    target = workspace / "output" / "judge_output.json"
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(judgeOutput), encoding="utf-8")
    normalized, diagnostics = CursorTransportNormalizer.normalize(
        rawProviderText=_fileEnvelope("output/judge_output.json"),
        workspaceRoot=workspace,
    )
    assert json.loads(normalized)["final_summary"]["summary"] == judgeOutput["final_summary"]["summary"]
    assert diagnostics.responseType == "file_reference"
    assert diagnostics.retrievalMethod == "local_workspace_read"
    assert diagnostics.bytesRecovered == target.stat().st_size


def test_file_reference_uses_sdk_download(workspace: Path):
    judgeOutput = buildCanonicalJudgeOutput()
    payload = json.dumps(judgeOutput).encode("utf-8")
    agent = _FakeAgent(artifacts={"output/judge_output.json": payload})
    normalized, diagnostics = CursorTransportNormalizer.normalize(
        rawProviderText=_fileEnvelope("output/judge_output.json"),
        workspaceRoot=workspace,
        agent=agent,
    )
    assert json.loads(normalized) == judgeOutput
    assert diagnostics.retrievalMethod == "cursor_sdk_download_artifact"


@pytest.mark.parametrize(
    ("payload", "stage"),
    [
        ({}, "missing_transport_version"),
        ({"transport_version": "2.0", "response_type": "inline_json", "content": {}}, "unsupported_transport_version"),
        ({"transport_version": "1.0"}, "missing_response_type"),
        ({"transport_version": "1.0", "response_type": "unknown"}, "unknown_response_type"),
        (
            {"transport_version": "1.0", "response_type": "inline_json"},
            "inline_response_missing_content",
        ),
        (
            {
                "transport_version": "1.0",
                "response_type": "inline_json",
                "content": {},
                "file_reference": {
                    "path": "x.json",
                    "format": "json",
                    "encoding": "utf-8",
                    "content_type": "application/json",
                },
            },
            "transport_envelope_unknown_field",
        ),
        (
            {"transport_version": "1.0", "response_type": "file_reference", "content": {}},
            "transport_envelope_unknown_field",
        ),
        (
            {"transport_version": "1.0", "response_type": "file_reference"},
            "file_response_missing_file_reference",
        ),
    ],
)
def test_invalid_transport_envelope(payload: dict, stage: str):
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportEnvelopeParser.parseEnvelopeDict(payload)
    assert exc_info.value.stage == stage


def test_missing_referenced_file(workspace: Path):
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportNormalizer.normalize(
            rawProviderText=_fileEnvelope("missing/output.json"),
            workspaceRoot=workspace,
        )
    assert exc_info.value.stage == "file_reference_missing_file"


def test_directory_instead_of_file(workspace: Path):
    directory = workspace / "output"
    directory.mkdir()
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportNormalizer.normalize(
            rawProviderText=_fileEnvelope("output"),
            workspaceRoot=workspace,
        )
    assert exc_info.value.stage in {"file_reference_directory_rejected", "file_reference_missing_file"}


def test_empty_file(workspace: Path):
    target = workspace / "output.json"
    target.write_text("", encoding="utf-8")
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportNormalizer.normalize(
            rawProviderText=_fileEnvelope("output.json"),
            workspaceRoot=workspace,
        )
    assert exc_info.value.stage == "file_reference_empty_file"


def test_malformed_file_json(workspace: Path):
    target = workspace / "output.json"
    target.write_text("{not json", encoding="utf-8")
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportNormalizer.normalize(
            rawProviderText=_fileEnvelope("output.json"),
            workspaceRoot=workspace,
        )
    assert exc_info.value.stage == "file_reference_malformed_json"


def test_multiple_json_objects(workspace: Path):
    target = workspace / "output.json"
    target.write_text('{"a": 1}{"b": 2}', encoding="utf-8")
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportNormalizer.normalize(
            rawProviderText=_fileEnvelope("output.json"),
            workspaceRoot=workspace,
        )
    assert exc_info.value.stage == "file_reference_multiple_json_objects"


def test_path_traversal_rejected(workspace: Path):
    with pytest.raises(CursorTransportError) as exc_info:
        CursorWorkspacePathResolver.resolve(workspaceRoot=workspace, relativePath="../outside.json")
    assert exc_info.value.stage == "file_reference_path_traversal_rejected"


def test_absolute_host_path_rejected(workspace: Path):
    with pytest.raises(CursorTransportError) as exc_info:
        CursorWorkspacePathResolver.resolve(workspaceRoot=workspace, relativePath="/tmp/output.json")
    assert exc_info.value.stage == "file_reference_absolute_path_rejected"


@pytest.mark.parametrize(
    "relativePath",
    [
        "C:\\temp\\result.json",
        "C:/temp/result.json",
        "\\\\server\\share\\result.json",
        "\\rooted\\result.json",
        "C:relative-path.json",
    ],
)
def test_cross_platform_absolute_paths_rejected(workspace: Path, relativePath: str):
    with pytest.raises(CursorTransportError) as exc_info:
        CursorWorkspacePathResolver.resolve(workspaceRoot=workspace, relativePath=relativePath)
    assert exc_info.value.stage == "file_reference_absolute_path_rejected"


def test_null_byte_in_path_rejected(workspace: Path):
    with pytest.raises(CursorTransportError) as exc_info:
        CursorWorkspacePathResolver.resolve(workspaceRoot=workspace, relativePath="output\u0000.json")
    assert exc_info.value.stage == "file_reference_null_byte_rejected"


def test_broken_symlink_rejected(workspace: Path):
    link = workspace / "broken.json"
    link.symlink_to(workspace / "missing.json")
    with pytest.raises(CursorTransportError) as exc_info:
        CursorWorkspacePathResolver.resolve(workspaceRoot=workspace, relativePath="broken.json")
    assert exc_info.value.stage == "file_reference_broken_symlink"


def test_valid_internal_symlink_allowed(workspace: Path):
    target = workspace / "output" / "judge_output.json"
    target.parent.mkdir(parents=True)
    target.write_text("{}", encoding="utf-8")
    link = workspace / "link.json"
    link.symlink_to(target)
    resolved = CursorWorkspacePathResolver.resolve(workspaceRoot=workspace, relativePath="link.json")
    assert resolved == target.resolve()


def test_unknown_top_level_envelope_key():
    judgeOutput = buildCanonicalJudgeOutput()
    payload = {
        "transport_version": "1.0",
        "response_type": "inline_json",
        "content": judgeOutput,
        "unexpected": True,
    }
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportEnvelopeParser.parseEnvelopeDict(payload)
    assert exc_info.value.stage == "transport_envelope_unknown_field"


def test_unknown_file_reference_key():
    payload = {
        "transport_version": "1.0",
        "response_type": "file_reference",
        "file_reference": {
            "path": "output.json",
            "format": "json",
            "encoding": "utf-8",
            "content_type": "application/json",
            "extra": "field",
        },
    }
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportEnvelopeParser.parseEnvelopeDict(payload)
    assert exc_info.value.stage == "file_reference_unknown_field"


def test_valid_envelope_with_exact_supported_keys(workspace: Path):
    judgeOutput = buildCanonicalJudgeOutput()
    normalized, diagnostics = CursorTransportNormalizer.normalize(
        rawProviderText=_inlineEnvelope(judgeOutput),
        workspaceRoot=workspace,
    )
    assert json.loads(normalized) == judgeOutput
    assert diagnostics.transportEnvelopeDetected is True


def test_arbitrary_json_not_treated_as_direct_judge_output(workspace: Path):
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportNormalizer.normalize(
            rawProviderText=json.dumps({"foo": "bar", "answer": 42}),
            workspaceRoot=workspace,
        )
    assert exc_info.value.stage == "unstructured_prose"


def test_symlink_escape_rejected(workspace: Path, tmp_path: Path):
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    link = workspace / "link.json"
    link.symlink_to(outside)
    with pytest.raises(CursorTransportError) as exc_info:
        CursorWorkspacePathResolver.resolve(workspaceRoot=workspace, relativePath="link.json")
    assert exc_info.value.stage == "file_reference_symlink_escape_rejected"


def test_legacy_prose_recovery_within_workspace(workspace: Path):
    judgeOutput = buildCanonicalJudgeOutput()
    target = workspace / "output" / "judge_output.json"
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(judgeOutput), encoding="utf-8")
    recovered = CursorLegacyProseRecovery.recover(
        rawText="The complete JSON is in output/judge_output.json",
        workspaceRoot=workspace,
        agent=None,
    )
    assert recovered is not None
    normalized, method = recovered
    assert json.loads(normalized) == judgeOutput
    assert method.startswith("legacy_")


def test_legacy_prose_unsafe_absolute_path_rejected(workspace: Path):
    recovered = CursorLegacyProseRecovery.recover(
        rawText="Read /etc/passwd for the answer",
        workspaceRoot=workspace,
        agent=None,
    )
    assert recovered is None


def test_unstructured_prose_fails(workspace: Path):
    with pytest.raises(CursorTransportError) as exc_info:
        CursorTransportNormalizer.normalize(
            rawProviderText="Please review the attached summary manually.",
            workspaceRoot=workspace,
        )
    assert exc_info.value.stage == "unstructured_prose"


def test_direct_judge_output_passthrough(workspace: Path):
    judgeOutput = buildCanonicalJudgeOutput()
    normalized, diagnostics = CursorTransportNormalizer.normalize(
        rawProviderText=json.dumps(judgeOutput),
        workspaceRoot=workspace,
    )
    assert json.loads(normalized) == judgeOutput
    assert diagnostics.normalizationMethod == "direct_judge_output"


def test_original_response_preserved_in_diagnostics(workspace: Path):
    judgeOutput = buildCanonicalJudgeOutput()
    providerText = _inlineEnvelope(judgeOutput)
    _, diagnostics = CursorTransportNormalizer.normalize(
        rawProviderText=providerText,
        workspaceRoot=workspace,
    )
    metadata = diagnostics.toProviderMetadata()
    assert metadata["original_raw_text"] == providerText
