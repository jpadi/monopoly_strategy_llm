"""Extract JSON from LLM responses."""

from __future__ import annotations

import json
import re
from typing import Any

from Monopoly.LlmEvaluation.Domain.Exception.LlmEvaluationErrors import JudgeOutputParseError


class JudgeResponseParser:
    _JSON_BLOCK = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)

    def parse(self, rawText: str) -> dict[str, Any]:
        text = rawText.strip()
        if not text:
            raise JudgeOutputParseError("Empty LLM response")

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        blockMatch = self._JSON_BLOCK.search(text)
        if blockMatch:
            try:
                parsed = json.loads(blockMatch.group(1))
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError as exc:
                raise JudgeOutputParseError(f"Invalid JSON in code block: {exc}") from exc

        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(text[start : end + 1])
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError as exc:
                raise JudgeOutputParseError(f"Could not extract JSON object: {exc}") from exc

        raise JudgeOutputParseError("LLM response did not contain a JSON object")
