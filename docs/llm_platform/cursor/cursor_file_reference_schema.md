# Cursor File Reference Transport Schema

Version: 1.0

Repository version: **1.2.0**

This document defines the **Cursor-specific response transport envelope**.

It is **not**:

- the canonical Judge Output;
- the canonical Judge Input;
- Static Algorithm Evidence;
- part of the Judge schema;
- part of the Static Evaluator schema.

It is exclusively the response transport contract used by the Cursor adapter before canonical Judge parsing.

Implementation: `Monopoly.LlmEvaluation.Infrastructure.Cursor`

---

## Transport envelope

Every Cursor provider response must be exactly one JSON object.

### Inline JSON transport

```json
{
  "transport_version": "1.0",
  "response_type": "inline_json",
  "content": {}
}
```

`content` must contain exactly one JSON object. For Judge calls, that object is the canonical Judge Output.

### Workspace file-reference transport

```json
{
  "transport_version": "1.0",
  "response_type": "file_reference",
  "file_reference": {
    "path": "output/judge_output.json",
    "format": "json",
    "encoding": "utf-8",
    "content_type": "application/json"
  }
}
```

The referenced file must contain exactly one JSON object. For Judge calls, that object is the canonical Judge Output.

---

## Required fields

| Field | Required | Rules |
|-------|----------|-------|
| `transport_version` | Yes | Must be `"1.0"` in version 1.2.0 |
| `response_type` | Yes | Must be `inline_json` or `file_reference` |
| `content` | Conditional | Required for `inline_json`; forbidden for `file_reference` |
| `file_reference` | Conditional | Required for `file_reference`; forbidden for `inline_json` |
| `file_reference.path` | Conditional | Workspace-relative path |
| `file_reference.format` | Conditional | Must be `json` |
| `file_reference.encoding` | Conditional | Must be `utf-8` |
| `file_reference.content_type` | Conditional | Must be `application/json` |

---

## Normative rules

- Unsupported `transport_version` values are rejected.
- Unknown `response_type` values are rejected.
- Unknown top-level transport envelope fields are rejected.
- Unknown `file_reference` object fields are rejected.
- `inline_json` and `file_reference` fields are mutually exclusive.
- The referenced file must not be empty.
- Multiple JSON values in the referenced file are forbidden.
- The file path must be relative to the authorized execution workspace.
- Arbitrary absolute host paths are rejected (POSIX, Windows drive-letter, UNC, drive-relative, and backslash-rooted forms).
- Null bytes in paths are rejected.
- Path traversal (`..`) is rejected.
- Broken symbolic links are rejected.
- Symbolic links that resolve inside the workspace are followed; links that escape the workspace are rejected.
- Directories are rejected.
- Missing files are rejected.
- The file must be read before workspace cleanup.
- The original Cursor response is retained in provider transport diagnostics.
- The normalized content is returned through canonical `LlmResponse.rawText`.
- Canonical Judge parsing and validation happen only after transport normalization.

---

## Normalized provider response

After transport normalization, `LlmResponse.rawText` contains the canonical Judge Output JSON text only.

Provider transport metadata is stored in `LlmResponse.providerMetadata` for artifact diagnostics. The Domain layer does not interpret that metadata.

---

## Related documents

- [cursor_response_transport.md](cursor_response_transport.md)
- [cursor_sdk_contract.md](cursor_sdk_contract.md)
