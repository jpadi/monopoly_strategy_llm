"""Unit tests for ArtifactStore helpers."""

from __future__ import annotations

import stat
from pathlib import Path

import pytest

from Monopoly.Shared.Infrastructure.ArtifactStore import (
    artifactDirectory,
    clearArtifactDirectory,
    writeArtifact,
    writeArtifactJson,
)


def test_clear_artifact_directory_removes_previous_contents(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "Monopoly.Shared.Infrastructure.ArtifactStore.artifactDirectory",
        lambda: tmp_path,
    )
    writeArtifact("nested/stale.txt", "old")
    assert (tmp_path / "nested" / "stale.txt").is_file()

    clearArtifactDirectory()

    assert tmp_path.is_dir()
    assert not (tmp_path / "nested").exists()

    writeArtifact("fresh.txt", "new")
    assert (tmp_path / "fresh.txt").read_text(encoding="utf-8") == "new"


def test_artifact_directory_resolves_under_project_root():
    root = artifactDirectory()
    assert root.name == "artifact"
    assert (root.parent / "CHANGELOG.md").is_file()


def test_clear_artifact_directory_empty_root(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "Monopoly.Shared.Infrastructure.ArtifactStore.artifactDirectory",
        lambda: tmp_path,
    )
    clearArtifactDirectory()
    assert tmp_path.is_dir()
    assert list(tmp_path.iterdir()) == []


def test_clear_artifact_directory_nested_tree(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "Monopoly.Shared.Infrastructure.ArtifactStore.artifactDirectory",
        lambda: tmp_path,
    )
    writeArtifactJson(
        "integration/LlmEvaluation/Infrastructure/Cursor/test/cursor_workspace/abc/provider_transport_diagnostics.json",
        {"response_type": "file_reference"},
    )
    writeArtifact(
        "integration/LlmEvaluation/Infrastructure/Cursor/test/initial_provider_response.txt",
        "transport envelope",
    )
    clearArtifactDirectory()
    assert tmp_path.is_dir()
    assert list(tmp_path.rglob("*")) == []


def test_clear_artifact_directory_missing_root(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "Monopoly.Shared.Infrastructure.ArtifactStore.artifactDirectory",
        lambda: tmp_path,
    )
    if tmp_path.exists():
        tmp_path.rmdir()
    clearArtifactDirectory()
    assert tmp_path.is_dir()


def test_clear_artifact_directory_partially_deleted_tree(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "Monopoly.Shared.Infrastructure.ArtifactStore.artifactDirectory",
        lambda: tmp_path,
    )
    nested = tmp_path / "nested" / "deep"
    nested.mkdir(parents=True)
    (nested / "keep.txt").write_text("x", encoding="utf-8")
    (nested / "remove.txt").write_text("y", encoding="utf-8")
    (nested / "remove.txt").unlink()
    clearArtifactDirectory()
    assert tmp_path.is_dir()
    assert list(tmp_path.rglob("*")) == []


def test_clear_artifact_directory_readonly_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "Monopoly.Shared.Infrastructure.ArtifactStore.artifactDirectory",
        lambda: tmp_path,
    )
    target = tmp_path / "readonly.txt"
    target.write_text("locked", encoding="utf-8")
    target.chmod(stat.S_IREAD)
    clearArtifactDirectory()
    assert tmp_path.is_dir()
    assert list(tmp_path.iterdir()) == []


def test_clear_artifact_directory_retries_transient_non_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "Monopoly.Shared.Infrastructure.ArtifactStore.artifactDirectory",
        lambda: tmp_path,
    )
    writeArtifact("nested/stale.txt", "old")
    originalRmtree = __import__("shutil").rmtree
    attempts = {"count": 0}

    def flaky_rmtree(path, onerror=None):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise OSError("Directory not empty")
        return originalRmtree(path, onerror=onerror)

    monkeypatch.setattr("Monopoly.Shared.Infrastructure.ArtifactStore.shutil.rmtree", flaky_rmtree)
    monkeypatch.setattr("Monopoly.Shared.Infrastructure.ArtifactStore.time.sleep", lambda _: None)

    clearArtifactDirectory()
    assert attempts["count"] == 2
    assert tmp_path.is_dir()
    assert list(tmp_path.iterdir()) == []


def test_clear_artifact_directory_raises_after_retry_exhaustion(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "Monopoly.Shared.Infrastructure.ArtifactStore.artifactDirectory",
        lambda: tmp_path,
    )
    writeArtifact("nested/stale.txt", "old")

    def always_fail_rmtree(path, onerror=None):
        raise OSError("Directory not empty")

    monkeypatch.setattr("Monopoly.Shared.Infrastructure.ArtifactStore.shutil.rmtree", always_fail_rmtree)
    monkeypatch.setattr("Monopoly.Shared.Infrastructure.ArtifactStore.time.sleep", lambda _: None)

    with pytest.raises(OSError, match="Directory not empty"):
        clearArtifactDirectory()
