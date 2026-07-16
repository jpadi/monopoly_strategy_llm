"""Tests for repository .env loading."""

from __future__ import annotations

import os

from Monopoly.Shared.Infrastructure.EnvironmentLoader import (
    cursorApiKeyConfigured,
    findRepositoryRoot,
    loadDotEnvFile,
    loadRepositoryEnvironment,
)


def test_find_repository_root():
    root = findRepositoryRoot()
    assert (root / "CHANGELOG.md").is_file()
    assert (root / "docs").is_dir()


def test_load_dotenv_does_not_override_existing(monkeypatch, tmp_path):
    envFile = tmp_path / ".env"
    envFile.write_text("CURSOR_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("CURSOR_API_KEY", "from-process")
    loaded = loadDotEnvFile(envFile)
    assert loaded["CURSOR_API_KEY"] == "from-file"
    assert os.environ["CURSOR_API_KEY"] == "from-process"


def test_load_dotenv_fills_missing_variables(tmp_path, monkeypatch):
    envFile = tmp_path / ".env"
    envFile.write_text("CURSOR_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.delenv("CURSOR_API_KEY", raising=False)
    loadDotEnvFile(envFile)
    assert os.environ["CURSOR_API_KEY"] == "from-file"


def test_repository_env_loader_uses_root_dotenv():
    root = loadRepositoryEnvironment()
    assert (root / ".env.example").is_file()
    # When .env exists locally, cursorApiKeyConfigured reflects loaded value after conftest import.
    assert isinstance(cursorApiKeyConfigured(), bool)
