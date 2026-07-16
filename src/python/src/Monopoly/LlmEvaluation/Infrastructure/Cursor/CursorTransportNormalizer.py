"""Normalize Cursor provider responses into canonical LlmResponse text."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorFileRetriever import CursorArtifactAgent, CursorFileRetriever
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorLegacyProseRecovery import CursorLegacyProseRecovery
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportConstants import (
    RESPONSE_TYPE_FILE_REFERENCE,
    RESPONSE_TYPE_INLINE_JSON,
)
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportDiagnostics import CursorTransportDiagnostics
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportEnvelopeParser import CursorTransportEnvelopeParser
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportError import CursorTransportError


class CursorTransportNormalizer:
    @staticmethod
    def normalize(
        *,
        rawProviderText: str,
        workspaceRoot: Path,
        agent: CursorArtifactAgent | None = None,
    ) -> tuple[str, CursorTransportDiagnostics]:
        originalRawText = rawProviderText or ""
        listedArtifactPaths = CursorFileRetriever._listArtifactPaths(agent)
        text = originalRawText.strip()

        if not text:
            diagnostics = CursorTransportDiagnostics(
                originalRawText=originalRawText,
                normalizationMethod="failed",
                failureStage="unstructured_prose",
                listedArtifactPaths=listedArtifactPaths,
            )
            raise CursorTransportError("Empty Cursor provider response", stage="unstructured_prose")

        payload = CursorTransportNormalizer._tryParseJsonObject(text)
        if payload is not None:
            if CursorTransportEnvelopeParser.looksLikeTransportEnvelope(payload):
                return CursorTransportNormalizer._normalizeEnvelope(
                    payload=payload,
                    originalRawText=originalRawText,
                    workspaceRoot=workspaceRoot,
                    agent=agent,
                    listedArtifactPaths=listedArtifactPaths,
                )
            if CursorTransportEnvelopeParser.looksLikeDirectJudgeOutput(payload):
                diagnostics = CursorTransportDiagnostics(
                    originalRawText=originalRawText,
                    normalizationMethod="direct_judge_output",
                    transportEnvelopeDetected=False,
                    listedArtifactPaths=listedArtifactPaths,
                )
                return json.dumps(payload), diagnostics

        legacy = CursorLegacyProseRecovery.recover(
            rawText=originalRawText,
            workspaceRoot=workspaceRoot,
            agent=agent,
        )
        if legacy is not None:
            normalized, method = legacy
            diagnostics = CursorTransportDiagnostics(
                originalRawText=originalRawText,
                normalizationMethod=method,
                legacyRecoveryUsed=True,
                listedArtifactPaths=listedArtifactPaths,
            )
            return normalized, diagnostics

        diagnostics = CursorTransportDiagnostics(
            originalRawText=originalRawText,
            normalizationMethod="failed",
            failureStage="unstructured_prose",
            listedArtifactPaths=listedArtifactPaths,
        )
        raise CursorTransportError(
            "Cursor provider response is not a valid transport envelope and legacy recovery failed",
            stage="unstructured_prose",
            details={"listed_artifact_paths": list(listedArtifactPaths)},
        )

    @staticmethod
    def _normalizeEnvelope(
        *,
        payload: dict[str, Any],
        originalRawText: str,
        workspaceRoot: Path,
        agent: CursorArtifactAgent | None,
        listedArtifactPaths: tuple[str, ...],
    ) -> tuple[str, CursorTransportDiagnostics]:
        envelope = CursorTransportEnvelopeParser.parseEnvelopeDict(payload)
        if envelope.responseType == RESPONSE_TYPE_INLINE_JSON:
            assert envelope.content is not None
            normalized = json.dumps(envelope.content)
            CursorTransportNormalizer._validateSingleJsonObject(normalized)
            diagnostics = CursorTransportDiagnostics(
                originalRawText=originalRawText,
                normalizationMethod="transport_inline_json",
                transportEnvelopeDetected=True,
                transportVersion=envelope.transportVersion,
                responseType=envelope.responseType,
                listedArtifactPaths=listedArtifactPaths,
            )
            return normalized, diagnostics

        assert envelope.fileReference is not None
        relativePath = envelope.fileReference["path"]
        recoveredText, retrievalMethod, fileExists, bytesRecovered = CursorFileRetriever.retrieveJsonText(
            workspaceRoot=workspaceRoot,
            relativePath=relativePath,
            agent=agent,
        )
        normalized = CursorTransportNormalizer._validateSingleJsonObject(recoveredText)
        diagnostics = CursorTransportDiagnostics(
            originalRawText=originalRawText,
            normalizationMethod="transport_file_reference",
            transportEnvelopeDetected=True,
            transportVersion=envelope.transportVersion,
            responseType=RESPONSE_TYPE_FILE_REFERENCE,
            workspaceRelativePath=relativePath,
            retrievalMethod=retrievalMethod,
            fileExists=fileExists,
            bytesRecovered=bytesRecovered,
            listedArtifactPaths=listedArtifactPaths,
        )
        return normalized, diagnostics

    @staticmethod
    def _tryParseJsonObject(text: str) -> dict[str, Any] | None:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None

    @staticmethod
    def _validateSingleJsonObject(text: str) -> str:
        stripped = text.strip()
        if not stripped:
            raise CursorTransportError("Recovered JSON file is empty", stage="file_reference_empty_file")
        decoder = json.JSONDecoder()
        try:
            payload, endIndex = decoder.raw_decode(stripped)
        except json.JSONDecodeError as exc:
            raise CursorTransportError(
                f"Recovered JSON file is malformed: {exc}",
                stage="file_reference_malformed_json",
            ) from exc
        if not isinstance(payload, dict):
            raise CursorTransportError(
                "Recovered JSON must be one object",
                stage="file_reference_malformed_json",
            )
        if stripped[endIndex:].strip():
            raise CursorTransportError(
                "Recovered JSON file contains multiple JSON values",
                stage="file_reference_multiple_json_objects",
            )
        return json.dumps(payload)
