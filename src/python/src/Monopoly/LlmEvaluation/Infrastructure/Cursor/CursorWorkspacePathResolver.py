"""Safe workspace-relative path resolution for Cursor file references."""

from __future__ import annotations

import os
import re
from pathlib import Path

from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportError import CursorTransportError

_WINDOWS_DRIVE_ABSOLUTE_PATTERN = re.compile(r"^[A-Za-z]:[/\\]")
_WINDOWS_DRIVE_RELATIVE_PATTERN = re.compile(r"^[A-Za-z]:[^/\\]")
_WINDOWS_BACKSLASH_ROOTED_PATTERN = re.compile(r"^\\[^\\]")


class CursorWorkspacePathResolver:
    @staticmethod
    def resolve(*, workspaceRoot: Path, relativePath: str) -> Path:
        normalized = relativePath.strip().replace("\\", "/")
        CursorWorkspacePathResolver._validateRelativePathInput(normalized)

        candidate = Path(normalized)
        workspaceResolved = workspaceRoot.resolve()
        candidatePath = workspaceRoot / candidate

        if candidatePath.is_symlink():
            if not candidatePath.exists():
                raise CursorTransportError(
                    "Broken symbolic links are not permitted in file_reference.path",
                    stage="file_reference_broken_symlink",
                    details={"path": normalized},
                )
            linkTarget = candidatePath.resolve()
            try:
                linkTarget.relative_to(workspaceResolved)
            except ValueError as exc:
                raise CursorTransportError(
                    "Symbolic link escapes the authorized execution workspace",
                    stage="file_reference_symlink_escape_rejected",
                    details={"path": normalized},
                ) from exc

        resolved = candidatePath.resolve()
        try:
            resolved.relative_to(workspaceResolved)
        except ValueError as exc:
            raise CursorTransportError(
                "File reference resolves outside the authorized execution workspace",
                stage="file_reference_outside_workspace",
                details={"path": normalized, "workspace": str(workspaceResolved)},
            ) from exc

        if resolved.is_dir():
            raise CursorTransportError(
                "File reference must point to a file, not a directory",
                stage="file_reference_directory_rejected",
                details={"path": normalized},
            )

        return resolved

    @staticmethod
    def normalizeRelativePath(*, workspaceRoot: Path, resolvedPath: Path) -> str:
        return os.path.relpath(resolvedPath, workspaceRoot.resolve())

    @staticmethod
    def _validateRelativePathInput(normalized: str) -> None:
        if not normalized:
            raise CursorTransportError(
                "File reference path is empty",
                stage="file_reference_path_invalid",
            )
        if "\x00" in normalized:
            raise CursorTransportError(
                "Null bytes are not permitted in file_reference.path",
                stage="file_reference_null_byte_rejected",
                details={"path": normalized},
            )
        if CursorWorkspacePathResolver._isForeignAbsolutePath(normalized):
            raise CursorTransportError(
                "Absolute host paths are not permitted in file_reference.path",
                stage="file_reference_absolute_path_rejected",
                details={"path": normalized},
            )
        if ".." in Path(normalized).parts:
            raise CursorTransportError(
                "Path traversal is not permitted in file_reference.path",
                stage="file_reference_path_traversal_rejected",
                details={"path": normalized},
            )

    @staticmethod
    def _isForeignAbsolutePath(normalized: str) -> bool:
        if normalized.startswith("/"):
            return True
        if normalized.startswith("//") or normalized.startswith("\\\\"):
            return True
        if _WINDOWS_DRIVE_ABSOLUTE_PATTERN.match(normalized):
            return True
        if _WINDOWS_DRIVE_RELATIVE_PATTERN.match(normalized):
            return True
        if _WINDOWS_BACKSLASH_ROOTED_PATTERN.match(normalized.replace("/", "\\")):
            return True
        candidate = Path(normalized)
        return candidate.is_absolute()
