"""Authorized execution workspace for Cursor provider calls."""

from __future__ import annotations

import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

from Monopoly.Shared.Infrastructure.ArtifactStore import currentArtifactSubpath, ensureArtifactDirectory


@dataclass
class CursorExecutionWorkspace:
    root: Path
    _temporaryDirectory: tempfile.TemporaryDirectory[str] | None = None

    @classmethod
    def create(cls) -> CursorExecutionWorkspace:
        subpath = currentArtifactSubpath()
        if subpath:
            root = ensureArtifactDirectory(*subpath.split("/"), "cursor_workspace", uuid.uuid4().hex[:12])
            return cls(root=root)
        temporaryDirectory = tempfile.TemporaryDirectory(prefix="monopoly_cursor_")
        return cls(root=Path(temporaryDirectory.name), _temporaryDirectory=temporaryDirectory)

    def cleanup(self) -> None:
        if self._temporaryDirectory is not None:
            self._temporaryDirectory.cleanup()
