"""Parse and validate Cursor transport envelopes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportConstants import (
    FILE_CONTENT_TYPE_JSON,
    FILE_ENCODING_UTF8,
    FILE_FORMAT_JSON,
    FILE_REFERENCE_ENVELOPE_KEYS,
    FILE_REFERENCE_OBJECT_KEYS,
    INLINE_ENVELOPE_KEYS,
    RESPONSE_TYPE_INLINE_JSON,
    SUPPORTED_RESPONSE_TYPES,
    SUPPORTED_TRANSPORT_VERSIONS,
    TRANSPORT_VERSION,
)
from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportError import CursorTransportError


@dataclass(frozen=True, slots=True)
class CursorTransportEnvelope:
    transportVersion: str
    responseType: str
    content: dict[str, Any] | None = None
    fileReference: dict[str, str] | None = None


class CursorTransportEnvelopeParser:
    @staticmethod
    def parseEnvelopeText(rawText: str) -> CursorTransportEnvelope:
        text = rawText.strip()
        if not text:
            raise CursorTransportError("Empty Cursor provider response", stage="unstructured_prose")

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise CursorTransportError(
                f"Cursor provider response is not valid transport JSON: {exc}",
                stage="invalid_transport_envelope",
            ) from exc

        if not isinstance(payload, dict):
            raise CursorTransportError(
                "Cursor transport envelope must be a JSON object",
                stage="invalid_transport_envelope",
            )

        return CursorTransportEnvelopeParser.parseEnvelopeDict(payload)

    @staticmethod
    def parseEnvelopeDict(payload: dict[str, Any]) -> CursorTransportEnvelope:
        if "transport_version" not in payload:
            raise CursorTransportError(
                "Cursor transport envelope missing transport_version",
                stage="missing_transport_version",
            )
        transportVersion = payload["transport_version"]
        if not isinstance(transportVersion, str):
            raise CursorTransportError(
                "Cursor transport envelope transport_version must be a string",
                stage="invalid_transport_version",
            )
        if transportVersion not in SUPPORTED_TRANSPORT_VERSIONS:
            raise CursorTransportError(
                f"Unsupported Cursor transport_version: {transportVersion}",
                stage="unsupported_transport_version",
                details={"transport_version": transportVersion, "supported": sorted(SUPPORTED_TRANSPORT_VERSIONS)},
            )

        responseType = payload.get("response_type")
        if not isinstance(responseType, str):
            raise CursorTransportError(
                "Cursor transport envelope missing response_type",
                stage="missing_response_type",
            )
        if responseType not in SUPPORTED_RESPONSE_TYPES:
            raise CursorTransportError(
                f"Unknown Cursor transport response_type: {responseType}",
                stage="unknown_response_type",
                details={"response_type": responseType},
            )

        content = payload.get("content")
        fileReference = payload.get("file_reference")
        if responseType == RESPONSE_TYPE_INLINE_JSON:
            CursorTransportEnvelopeParser._rejectUnknownKeys(payload, INLINE_ENVELOPE_KEYS)
            if fileReference is not None:
                raise CursorTransportError(
                    "inline_json transport must not include file_reference",
                    stage="inline_response_contains_file_reference",
                )
            if not isinstance(content, dict):
                raise CursorTransportError(
                    "inline_json transport requires content object",
                    stage="inline_response_missing_content",
                )
            return CursorTransportEnvelope(
                transportVersion=transportVersion,
                responseType=responseType,
                content=content,
            )

        CursorTransportEnvelopeParser._rejectUnknownKeys(payload, FILE_REFERENCE_ENVELOPE_KEYS)
        if content is not None:
            raise CursorTransportError(
                "file_reference transport must not include content",
                stage="file_response_contains_content",
            )
        if not isinstance(fileReference, dict):
            raise CursorTransportError(
                "file_reference transport requires file_reference object",
                stage="file_response_missing_file_reference",
            )
        CursorTransportEnvelopeParser._validateFileReference(fileReference)
        normalizedReference = {
            "path": str(fileReference["path"]),
            "format": str(fileReference["format"]),
            "encoding": str(fileReference["encoding"]),
            "content_type": str(fileReference["content_type"]),
        }
        return CursorTransportEnvelope(
            transportVersion=transportVersion,
            responseType=responseType,
            fileReference=normalizedReference,
        )

    @staticmethod
    def _validateFileReference(fileReference: dict[str, Any]) -> None:
        unknownKeys = set(fileReference) - FILE_REFERENCE_OBJECT_KEYS
        if unknownKeys:
            raise CursorTransportError(
                f"file_reference contains unsupported fields: {sorted(unknownKeys)}",
                stage="file_reference_unknown_field",
                details={"unknown_fields": sorted(unknownKeys)},
            )
        for field in ("path", "format", "encoding", "content_type"):
            if field not in fileReference:
                raise CursorTransportError(
                    f"file_reference missing {field}",
                    stage="file_response_missing_file_reference",
                )
        if fileReference["format"] != FILE_FORMAT_JSON:
            raise CursorTransportError(
                "file_reference.format must be json",
                stage="unsupported_format",
            )
        if fileReference["encoding"] != FILE_ENCODING_UTF8:
            raise CursorTransportError(
                "file_reference.encoding must be utf-8",
                stage="unsupported_encoding",
            )
        if fileReference["content_type"] != FILE_CONTENT_TYPE_JSON:
            raise CursorTransportError(
                "file_reference.content_type must be application/json",
                stage="incorrect_content_type",
            )

    @staticmethod
    def _rejectUnknownKeys(payload: dict[str, Any], allowedKeys: frozenset[str]) -> None:
        unknownKeys = set(payload) - allowedKeys
        if unknownKeys:
            raise CursorTransportError(
                f"Cursor transport envelope contains unsupported fields: {sorted(unknownKeys)}",
                stage="transport_envelope_unknown_field",
                details={"unknown_fields": sorted(unknownKeys)},
            )

    @staticmethod
    def looksLikeTransportEnvelope(payload: dict[str, Any]) -> bool:
        return "transport_version" in payload and "response_type" in payload

    @staticmethod
    def looksLikeDirectJudgeOutput(payload: dict[str, Any]) -> bool:
        from Monopoly.LlmEvaluation.Infrastructure.Cursor.CursorTransportConstants import REQUIRED_JUDGE_SECTIONS

        return REQUIRED_JUDGE_SECTIONS.issubset(payload.keys())

    @staticmethod
    def defaultTransportVersion() -> str:
        return TRANSPORT_VERSION
