"""Project-root artifact directory helpers."""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_CLEAR_MAX_RETRIES = 3
_ARTIFACT_CLEAR_RETRY_DELAY_SECONDS = 0.05


def findProjectRoot() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "CHANGELOG.md").is_file() and (candidate / "docs").is_dir():
            return candidate
    raise RuntimeError("Monopoly project root not found")


def artifactDirectory() -> Path:
    return findProjectRoot() / "artifact"


def _removeReadonlyArtifactPath(func, path: str, excInfo) -> None:
    os.chmod(path, stat.S_IWUSR | stat.S_IREAD)
    func(path)


def clearArtifactDirectory() -> None:
    """Remove all contents under artifact/ and recreate the directory.

    Uses bounded retries for transient non-empty directory conditions that can
    occur when nested integration artifact trees are still flushing to disk.
    """
    root = artifactDirectory()
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
        return

    lastError: OSError | None = None
    for attempt in range(_ARTIFACT_CLEAR_MAX_RETRIES):
        try:
            shutil.rmtree(root, onerror=_removeReadonlyArtifactPath)
            lastError = None
            break
        except OSError as exc:
            lastError = exc
            if attempt + 1 < _ARTIFACT_CLEAR_MAX_RETRIES:
                time.sleep(_ARTIFACT_CLEAR_RETRY_DELAY_SECONDS)
    if lastError is not None:
        raise lastError
    root.mkdir(parents=True, exist_ok=True)


def artifactRelativePathFromPytestNode(nodeid: str) -> str:
    """Map pytest nodeid to artifact path mirroring test/python layout and class/method."""
    if "::" not in nodeid:
        relative = nodeid.replace("\\", "/")
        if relative.startswith("test/python/"):
            relative = relative.removeprefix("test/python/")
        return relative.removesuffix(".py")

    filePart, testPart = nodeid.split("::", 1)
    relativeFile = filePart.replace("\\", "/")
    if relativeFile.startswith("test/python/"):
        relativeFile = relativeFile.removeprefix("test/python/")
    relativeFile = relativeFile.removesuffix(".py")

    testSegments = testPart.split("::")
    testPath = "/".join(testSegments)

    paramMatch = re.match(r"^(?P<name>[^[]+)(?:\[(?P<param>.+)\])?$", testPath)
    if paramMatch is None:
        return f"{relativeFile}/{testPath}"

    name = paramMatch.group("name")
    param = paramMatch.group("param")
    if param:
        return f"{relativeFile}/{name}/{param}"
    return f"{relativeFile}/{name}"


def currentArtifactSubpath() -> str | None:
    value = os.environ.get("MONOPOLY_ARTIFACT_SUBPATH", "").strip()
    return value or None


def ensureArtifactDirectory(*subpaths: str) -> Path:
    target = artifactDirectory().joinpath(*subpaths) if subpaths else artifactDirectory()
    target.mkdir(parents=True, exist_ok=True)
    return target


def writeArtifact(relativePath: str, content: str | bytes) -> Path:
    path = artifactDirectory() / relativePath
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        path.write_text(content, encoding="utf-8")
    else:
        path.write_bytes(content)
    return path


def writeArtifactJson(relativePath: str, payload: Any) -> Path:
    return writeArtifact(relativePath, json.dumps(payload, indent=2, default=str))


def timestampSlug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")  # noqa: UP017
