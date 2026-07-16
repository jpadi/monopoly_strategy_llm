# LLM Platform

This folder exists because **how the Judge receives specification files depends on the LLM client and API** — not on evaluation rules.

Evaluation rules live in `docs/llm_evaluator/` and `docs/static_evaluator/`. Those documents are the same for every provider.

Transport and delivery instructions live here. They are appended to the **initial prompt** (instructions message) so the Judge knows how to read the files the host sends for **that** integration.

---

## Why a separate folder

API-based LLM clients differ in meaningful ways:

- some accept only a single text prompt;
- some support native file upload;
- some require inline content with headers;
- some use separate system and user messages.

Those differences affect **how the host attaches files**, not **what the Judge evaluates**. Keeping platform notes out of `docs/llm_evaluator/` avoids mixing transport details with normative Judge rules.

---

## Contract: paths, not inlined bodies

`JudgePromptBuilder` passes an `LlmRequest` with:

- **`instructionFilePaths`** — repository-relative paths loaded by the client into the instructions message (always includes `00_initial_prompt.md` and shared docs from this folder)
- **`attachmentFilePaths`** — repository-relative paths for specification files the client must deliver as attachments
- **`taskPrompt`** — evaluation context, input JSON, and delivery manifest (no specification bodies)
- **`specificationBundle`** — file bytes for attachment paths

Each **`LlmClient`** reads those paths, loads content, and delivers it using the mechanism appropriate for that API (inline headers, native upload, etc.).

---

## Stable Judge bundles vs conditional static bundle

The complete `docs/llm_evaluator/` set is **stable across all Judge runtime modes**.

The `docs/static_evaluator/` set is added **only when the host resolves `execution_mode = LLM_STATIC_FALLBACK`** for the current request.

Fallback may be configured or authorized in the input without triggering static specification delivery. Delivery occurs when the reference host determines the Judge must execute LLM Static Fallback.

Platform delivery instructions vary by selected LLM client. They do **not** reduce the mandatory `docs/llm_evaluator/` bundle.

---

## How documents are used

The client builds the instructions message in this order:

1. **`docs/llm_evaluator/00_initial_prompt.md`** — entry workflow (always)
2. **Shared platform docs from this folder** — apply to every API client (today: [file_attachment_standard.md](file_attachment_standard.md))
3. **Client-specific docs from this folder** — when the active `LlmClient` needs extra explanation

The task message carries the delivery manifest, evaluation input JSON, and attached specification files.

The delivery manifest lists **every instruction and attachment path** delivered for the request.

---

## What belongs here

| Document | Scope |
|----------|--------|
| [file_attachment_standard.md](file_attachment_standard.md) | Shared inline attachment format (path headers + verbatim file content) |
| [cursor/](cursor/README.md) | Cursor adapter SDK contract, transport envelope, and response normalization |
| Future client-specific folders | How that provider’s adapter loads paths and delivers files |

Do **not** put evaluation rules, schemas, or Judge workflow changes in this folder.

---

## Reference implementation (v1.2.0)

- `JudgePromptBuilder` sets `instructionFilePaths` and `attachmentFilePaths` and builds the delivery manifest.
- `LlmPromptAssembler` + `CursorLlmClient` load paths and send one combined prompt via the Cursor API using inline headers from the attachment standard.
- `CursorLlmClient` appends a Cursor-specific transport instruction and normalizes Cursor responses before canonical Judge parsing.
- Request artifacts record instruction paths, attachment paths, manifest paths, provider transport diagnostics, and content hashes (no credentials).

---

## Related documents

- [cursor/README.md](cursor/README.md)
- [cursor/cursor_response_transport.md](cursor/cursor_response_transport.md)
