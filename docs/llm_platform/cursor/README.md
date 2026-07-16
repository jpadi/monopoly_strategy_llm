# Cursor Platform Integration

Version: 1.0

Cursor-specific transport behavior for the reference Python implementation lives in this folder.

These documents describe **how the Cursor adapter delivers and recovers Judge output**. They do **not** change Judge evaluation rules.

Normative Judge rules remain in `docs/llm_evaluator/`.

---

## Documents

| Document | Purpose |
|----------|---------|
| [cursor_sdk_contract.md](cursor_sdk_contract.md) | Installed SDK version and officially exposed public contract |
| [cursor_response_transport.md](cursor_response_transport.md) | Transport normalization flow and retrieval methods |
| [cursor_file_reference_schema.md](cursor_file_reference_schema.md) | Strict Cursor transport envelope schema |

---

## Scope

Cursor transport behavior is implemented only in:

```text
src/python/src/Monopoly/LlmEvaluation/Infrastructure/Cursor/
```

The Judge Domain and Application layers consume canonical `LlmResponse.rawText` only.

---

## Environment

Repository environment loading is documented in [cursor_response_transport.md](cursor_response_transport.md#environment-configuration).

See repository root `.env.example` for supported variables in version **1.2.0**:

| Variable | Scope |
|----------|-------|
| `CURSOR_API_KEY` | Production bootstrap and integration tests |
| `MONOPOLY_KEEP_ARTIFACTS` | Pytest only — skip artifact directory clearing |
| `CURSOR_JUDGE_MODEL` | Integration tests only — production uses `llm_execution.model` |
| `CURSOR_ASSESSOR_MODEL` | Reserved (not wired in 1.2.0) |
| `LLM_REQUEST_TIMEOUT_SECONDS` | Reserved (not wired in 1.2.0) |
