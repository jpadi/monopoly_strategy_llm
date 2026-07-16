"""Cursor transport envelope constants."""

from __future__ import annotations

TRANSPORT_VERSION = "1.0"
SUPPORTED_TRANSPORT_VERSIONS = frozenset({TRANSPORT_VERSION})

RESPONSE_TYPE_INLINE_JSON = "inline_json"
RESPONSE_TYPE_FILE_REFERENCE = "file_reference"
SUPPORTED_RESPONSE_TYPES = frozenset({RESPONSE_TYPE_INLINE_JSON, RESPONSE_TYPE_FILE_REFERENCE})

INLINE_ENVELOPE_KEYS = frozenset({"transport_version", "response_type", "content"})
FILE_REFERENCE_ENVELOPE_KEYS = frozenset({"transport_version", "response_type", "file_reference"})
FILE_REFERENCE_OBJECT_KEYS = frozenset({"path", "format", "encoding", "content_type"})

FILE_FORMAT_JSON = "json"
FILE_ENCODING_UTF8 = "utf-8"
FILE_CONTENT_TYPE_JSON = "application/json"

REQUIRED_JUDGE_SECTIONS = frozenset(
    {
        "competitive_classification",
        "competitive_evaluation",
        "supporting_evidence",
        "static_analysis_result",
        "decision_pattern_analysis",
        "confidence_assessment",
        "final_summary",
    }
)
