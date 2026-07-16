# File Attachment Standard

Version: 1.0

Shared delivery format for every API client. See [README.md](README.md) for why this folder exists.

The `LlmClient` receives **`attachmentFilePaths`** and loads each file’s content. When inline delivery is required, wrap content using these headers:

---

## Headers

Each file uses a begin and end header on their own lines. `{relative_path}` is the repository-relative path (forward slashes).

**Begin:**

```text
--- BEGIN ATTACHED FILE: {relative_path} ---
```

**End:**

```text
--- END ATTACHED FILE: {relative_path} ---
```

---

## Rules

- The text between the headers is the **verbatim file body** (UTF-8).
- Headers are not part of the file content.
- One file per envelope.
- Attach only paths listed in `attachmentFilePaths` / the structure manifest, in manifest read order.

---

## Example

```text
--- BEGIN ATTACHED FILE: docs/llm_evaluator/01_judge.md ---
# Monopoly Trade Evaluation Judge Specification
...
--- END ATTACHED FILE: docs/llm_evaluator/01_judge.md ---
```

Treat the inner content as if the file existed at `{relative_path}`.

Attached files appear under **`## Attached specification files`** in the assembled prompt.
