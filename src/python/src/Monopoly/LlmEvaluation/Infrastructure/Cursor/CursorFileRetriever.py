"""Retrieve referenced files through the Cursor SDK artifact API or local workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportError import CursorTransportError
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorWorkspacePathResolver import CursorWorkspacePathResolver


class CursorArtifactAgent(Protocol):
    def list_artifacts(self) -> list[Any]: ...

    def download_artifact(self, path: str) -> bytes: ...


class CursorFileRetriever:
    @staticmethod
    def retrieveJsonText(
        *,
        workspaceRoot: Path,
        relativePath: str,
        agent: CursorArtifactAgent | None,
    ) -> tuple[str, str, bool, int]:
        listedPaths = CursorFileRetriever._listArtifactPaths(agent)
        resolvedPath = CursorWorkspacePathResolver.resolve(workspaceRoot=workspaceRoot, relativePath=relativePath)

        if agent is not None and relativePath in listedPaths:
            try:
                payload = agent.download_artifact(relativePath)
            except Exception as exc:
                raise CursorTransportError(
                    f"Cursor SDK artifact download failed: {exc}",
                    stage="file_reference_sdk_download_failed",
                    details={"path": relativePath},
                ) from exc
            text = payload.decode("utf-8")
            return text, "cursor_sdk_download_artifact", True, len(payload)

        if not resolvedPath.is_file():
            raise CursorTransportError(
                "Referenced workspace file does not exist",
                stage="file_reference_missing_file",
                details={"path": relativePath, "listed_artifact_paths": listedPaths},
            )

        payload = resolvedPath.read_bytes()
        if not payload:
            raise CursorTransportError(
                "Referenced workspace file is empty",
                stage="file_reference_empty_file",
                details={"path": relativePath},
            )
        return payload.decode("utf-8"), "local_workspace_read", True, len(payload)

    @staticmethod
    def _listArtifactPaths(agent: CursorArtifactAgent | None) -> tuple[str, ...]:
        if agent is None:
            return ()
        try:
            artifacts = agent.list_artifacts()
        except Exception:
            return ()
        return tuple(getattr(item, "path", "") for item in artifacts if getattr(item, "path", ""))
