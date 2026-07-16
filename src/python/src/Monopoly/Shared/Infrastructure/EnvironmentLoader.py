"""Load repository environment variables from `.env` at the project root."""

from __future__ import annotations

import os
from pathlib import Path


def findRepositoryRoot(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "CHANGELOG.md").is_file() and (candidate / "docs").is_dir():
            return candidate
    raise RuntimeError("Monopoly repository root not found")


def loadDotEnvFile(path: Path, *, overrideExisting: bool = False) -> dict[str, str]:
    """Parse a dotenv file into key/value pairs and optionally export them to os.environ."""
    loaded: dict[str, str] = {}
    if not path.is_file():
        return loaded

    for rawLine in path.read_text(encoding="utf-8").splitlines():
        line = rawLine.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        loaded[key] = value
        if overrideExisting or key not in os.environ:
            os.environ[key] = value
    return loaded


def loadRepositoryEnvironment(*, repoRoot: Path | None = None, overrideExisting: bool = False) -> Path:
    """Load `.env` from the repository root. Existing process environment wins by default."""
    root = repoRoot or findRepositoryRoot()
    loadDotEnvFile(root / ".env", overrideExisting=overrideExisting)
    return root


def cursorApiKeyConfigured() -> bool:
    return bool(os.environ.get("CURSOR_API_KEY", "").strip())
