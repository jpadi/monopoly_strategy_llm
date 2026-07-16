"""Structured Judge output validation error records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JudgeValidationErrorRecord:
    path: str
    code: str
    message: str

    def toDict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


def mergeValidationErrors(
    messages: list[str],
    records: list[JudgeValidationErrorRecord],
) -> tuple[tuple[str, ...], tuple[JudgeValidationErrorRecord, ...]]:
    return tuple(messages), tuple(records)
