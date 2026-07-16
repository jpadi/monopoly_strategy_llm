# Cursor SDK Contract

Version: 1.0

Repository version: **1.2.0**

This document records the **installed Cursor SDK contract** used by the reference Python implementation.

It distinguishes:

1. **Official Cursor SDK behavior** — stable public API exposed by the installed package.
2. **Observed agent behavior** — patterns seen during live runs but not guaranteed by the SDK.
3. **Repository workaround** — normalization implemented by this repository.

---

## Installed SDK

The reference implementation targets the optional Python extra:

```text
cursor-sdk>=0.1.0
```

Verified during development against:

```text
cursor-sdk 0.1.9
```

Package entry point:

```python
from cursor_sdk import Agent, AgentOptions
```

---

## Official SDK behavior used by this repository

The reference `CursorLlmClient` uses the following **public SDK surface**:

| Capability | SDK API | Purpose |
|------------|---------|---------|
| One-shot agent call | `Agent.create(...)` + `agent.send(...).wait()` | Execute the Judge prompt |
| Final text | `RunResult.result` | Provider response text |
| Run status | `RunResult.status` | Finish reason mapping |
| Token usage | `RunResult.usage` | Optional usage metadata |
| Run identifier | `RunResult.id` | Diagnostics only |
| Workspace root | `AgentOptions.local.cwd` | Authorized execution workspace |
| Artifact listing | `agent.list_artifacts()` | Discover files created during the run |
| Artifact download | `agent.download_artifact(path)` | Retrieve referenced workspace files through the SDK |

The SDK exposes `SdkArtifact` with:

```text
path
size_bytes
updated_at
```

The reference implementation reads artifacts **before** calling `agent.close()`.

---

## Official SDK behavior not used for Judge semantics

The following SDK capabilities exist but are **not** part of Judge evaluation logic:

- cloud repository options;
- MCP server configuration;
- custom tool callbacks;
- message history inspection beyond the final run result.

They may be used only for transport diagnostics or future provider features.

---

## Observed agent behavior (not an official SDK contract)

During live integration tests, the Cursor Agent has been observed to:

- return prose instead of JSON when output is large;
- mention workspace file paths informally in prose;
- write large JSON results to workspace files instead of returning them inline in `RunResult.result`.

These behaviors are **not** documented here as stable Cursor SDK guarantees.

They are handled by the repository transport layer documented in [cursor_response_transport.md](cursor_response_transport.md).

---

## Repository workaround (version 1.2.0)

The reference implementation requires a **Cursor transport envelope** appended by `CursorTransportInstruction` immediately before the SDK call.

If the agent returns unstructured prose, a **legacy experimental compatibility** path may recover JSON from workspace files or SDK artifacts. See [cursor_response_transport.md](cursor_response_transport.md#legacy-experimental-compatibility).

Legacy recovery is secondary to the structured transport envelope and remains bounded to the authorized execution workspace.

---

## What the SDK does not guarantee

Based on inspection of `cursor-sdk 0.1.9`:

- The SDK does **not** automatically convert large Judge output into a transport envelope.
- The SDK does **not** guarantee that `RunResult.result` always contains complete JSON.
- The SDK does **not** expose a dedicated “Judge output artifact” type separate from workspace artifacts.

File recovery therefore depends on:

1. the structured transport envelope returned in `RunResult.result`; or
2. bounded legacy recovery using `list_artifacts()` / `download_artifact()` / authorized workspace reads.

---

## Related documents

- [cursor_response_transport.md](cursor_response_transport.md)
- [cursor_file_reference_schema.md](cursor_file_reference_schema.md)
- [../README.md](../README.md)
