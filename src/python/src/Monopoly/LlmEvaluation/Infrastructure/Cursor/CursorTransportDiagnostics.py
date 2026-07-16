"""Cursor transport diagnostics for artifact recording."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CursorTransportDiagnostics:
    originalRawText: str
    normalizationMethod: str
    transportEnvelopeDetected: bool = False
    transportVersion: str | None = None
    responseType: str | None = None
    workspaceRelativePath: str | None = None
    retrievalMethod: str | None = None
    fileExists: bool | None = None
    bytesRecovered: int | None = None
    legacyRecoveryUsed: bool = False
    failureStage: str | None = None
    listedArtifactPaths: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)

    def toProviderMetadata(self) -> dict[str, Any]:
        return {
            "provider": "cursor",
            "original_raw_text": self.originalRawText,
            "normalization_method": self.normalizationMethod,
            "transport_envelope_detected": self.transportEnvelopeDetected,
            "transport_version": self.transportVersion,
            "response_type": self.responseType,
            "workspace_relative_path": self.workspaceRelativePath,
            "retrieval_method": self.retrievalMethod,
            "file_exists": self.fileExists,
            "bytes_recovered": self.bytesRecovered,
            "legacy_recovery_used": self.legacyRecoveryUsed,
            "failure_stage": self.failureStage,
            "listed_artifact_paths": list(self.listedArtifactPaths),
            **self.extra,
        }
