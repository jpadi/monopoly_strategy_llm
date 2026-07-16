# Cursor Response Transport

Version: 1.0

Repository version: **1.2.0**

This document describes Cursor-specific **response transport normalization** for the reference Python implementation.

Normative Judge rules remain in `docs/llm_evaluator/`.

---

## Environment configuration

The reference implementation loads repository environment variables from:

```text
<repository-root>/.env
```

Loading occurs when:

- `Monopoly.bootstrap` is imported; and
- pytest starts (`test/python/conftest.py` loads `.env` before integration tests).

**Precedence:** existing process environment variables win. Values from `.env` fill only variables that are not already set in the process environment.

Integration tests run when `CURSOR_API_KEY` is configured through either mechanism. They skip only when the key is genuinely unavailable.

Supported variables for version **1.2.0** are listed in repository root `.env.example`.

---

## Transport flow

```text
Cursor Agent response (RunResult.result)
    ↓
Cursor transport-envelope parser
    ↓
inline_json OR validated workspace file reference
    ↓
canonical provider-neutral LlmResponse.rawText
    ↓
JudgeResponseParser
    ↓
JudgeOutputValidator
```

Cursor transport behavior exists only in:

```text
src/python/src/Monopoly/LlmEvaluation/Infrastructure/Cursor/
```

The Judge Domain and Application layers do not inspect Cursor paths, SDK artifacts, or transport envelopes.

---

## Provider instruction

`CursorLlmClient` appends `CursorTransportInstruction` immediately before the SDK call.

That instruction requires exactly one transport envelope JSON object and forbids prose, Markdown, informal file-reference sentences, and absolute host paths.

The instruction is **not** part of the Judge specification bundle and is **not** added by `JudgePromptBuilder`.

---

## Structured transport envelope

The normative schema is defined in [cursor_file_reference_schema.md](cursor_file_reference_schema.md).

Supported response types:

- `inline_json`
- `file_reference`

---

## File retrieval

For `file_reference` responses, the adapter retrieves file content in this order:

1. Call `list_artifacts()`.
2. If the referenced path is listed, use `download_artifact(path)`.
3. Otherwise, read from the authorized local execution workspace (`AgentOptions.local.cwd`).

**Live integration runs in version 1.2.0** exercised step 3 (`local_workspace_read`) when `list_artifacts()` returned an empty list. SDK artifact download is supported production code and covered by mocked unit tests; it is not claimed as the path used by successful live runs unless a live run lists the referenced path.

The agent remains open until retrieval completes. Workspace cleanup occurs only after normalization succeeds or fails.

---

## Workspace lifecycle

Each call to `CursorLlmClient.complete()` creates its own authorized execution workspace. This applies to:

- the initial Judge request; and
- the single repair request (when repair is triggered).

Lifecycle per call:

1. Create workspace (`CursorExecutionWorkspace.create()`).
2. Materialize specification content through the combined prompt (not written into the workspace by default).
3. Execute the Cursor SDK agent with `local.cwd` set to the workspace root.
4. Normalize the provider response (transport envelope, optional direct canonical JSON, or legacy experimental recovery).
5. Retrieve referenced files from the **same call's workspace** before cleanup.
6. Capture transport diagnostics in `LlmResponse.providerMetadata` and optional artifact files.
7. Clean up temporary workspaces (artifact-subpath workspaces persist for integration diagnostics).

A repair response using `file_reference` must reference a file in the **repair call's workspace**, not the initial call's workspace. Initial and repair workspaces are always distinct.

---

## Workspace security

Each Cursor call uses an authorized execution workspace:

- under the current pytest artifact subpath when present; otherwise
- a temporary directory destroyed after the call.

Rules:

- `file_reference.path` must be workspace-relative.
- Absolute host paths are rejected (POSIX, Windows drive-letter, UNC, drive-relative, and backslash-rooted forms).
- Null bytes in paths are rejected.
- Path traversal is rejected.
- Broken symbolic links are rejected.
- Symbolic links that resolve inside the workspace are followed; links that escape the workspace are rejected.
- Directories are rejected.

---

## Direct canonical Judge JSON (`direct_judge_output`)

When the provider returns a JSON object that is **not** a transport envelope but contains all seven canonical Judge top-level sections, the adapter accepts it as bounded compatibility behavior (`direct_judge_output`).

- This path is secondary to the structured transport envelope.
- Its use is recorded in transport diagnostics (`normalization_method = direct_judge_output`).
- Canonical Judge parsing and validation remain strict; arbitrary JSON objects are not accepted.
- This behavior is Cursor adapter infrastructure only and is not part of Judge specifications.

---

## Diagnostics

When transport normalization runs, the adapter stores diagnostics in `LlmResponse.providerMetadata`, including:

- original provider text;
- normalization method;
- transport envelope detection;
- response type;
- workspace-relative path;
- retrieval method;
- bytes recovered;
- listed artifact paths;
- legacy recovery usage.

Artifacts may also record:

```text
provider_transport_diagnostics.json
initial_provider_response.txt
```

---

## Legacy experimental compatibility

If the provider response is not a valid transport envelope and not direct canonical Judge JSON, the adapter may attempt **legacy experimental compatibility** recovery.

Legacy recovery:

- applies only in `Infrastructure/Cursor/`;
- is secondary to the structured transport envelope;
- scans SDK artifact paths and bounded workspace-relative filenames mentioned in prose;
- rejects absolute host paths;
- records `legacy_recovery_used = true` in diagnostics when used.

Legacy recovery is **not** official Cursor SDK behavior.

---

## Host response parsing (reference Python)

The reference `JudgeResponseParser` lives in the Domain layer and applies **host-side lenience** when extracting JSON from already-normalized provider text:

1. Accept a response that is already one JSON object.
2. Otherwise, extract JSON from a Markdown fenced code block when present.
3. Otherwise, extract the outermost `{ ... }` substring when present.

This lenience is **not** part of the Judge specification. Canonical Judge validation remains strict.

---

## Mandatory Judge output

Regardless of Cursor transport behavior, the Judge MUST still comply with:

- `docs/llm_evaluator/06_output_schema.md` — Mandatory Response Format
- `docs/llm_evaluator/00_initial_prompt.md` — inline JSON requirement for the Judge role

Transport normalization does not weaken schema validation and does not accept invalid Judge output.

---

## Known external provider limitation in version 1.2.0

If the Cursor Agent returns unstructured prose **and** does not create a retrievable workspace artifact or valid transport envelope, transport normalization fails and the existing single repair attempt proceeds using canonical Judge repair rules.

This limitation is external to the repository when the provider neither returns the envelope nor creates retrievable workspace output.

---

## Related documents

- [cursor_sdk_contract.md](cursor_sdk_contract.md)
- [cursor_file_reference_schema.md](cursor_file_reference_schema.md)
- [README.md](README.md)
