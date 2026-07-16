"""Provider-specific Cursor transport instruction appended before SDK calls."""

from __future__ import annotations

CURSOR_TRANSPORT_INSTRUCTION = """\
## Cursor Response Transport (Provider-Specific)

Return exactly one Cursor transport envelope as JSON.

Use `response_type = inline_json` when the complete result is returned directly in `content`.

Use `response_type = file_reference` only when the complete result has been written inside the
authorized execution workspace.

When using `file_reference`, return the exact workspace-relative path in `file_reference.path`.

Required envelope shape:

```json
{
  "transport_version": "1.0",
  "response_type": "inline_json",
  "content": {}
}
```

or:

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

Rules:

- Return the transport envelope only. Do not return prose, Markdown, or informal sentences pointing to a file.
- Do not return an absolute host path.
- The referenced file must contain exactly one JSON object.
- `content` and `file_reference` are mutually exclusive.
"""


class CursorTransportInstruction:
    @staticmethod
    def appendToPrompt(prompt: str) -> str:
        if CURSOR_TRANSPORT_INSTRUCTION.strip() in prompt:
            return prompt
        return f"{prompt.rstrip()}\n\n{CURSOR_TRANSPORT_INSTRUCTION}"
