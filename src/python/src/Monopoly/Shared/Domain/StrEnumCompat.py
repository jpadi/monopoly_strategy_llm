"""StrEnum compatibility for Python 3.10 (stdlib StrEnum requires 3.11+)."""

from enum import Enum


class StrEnum(str, Enum):  # noqa: UP042
    """String enum compatible with enum.StrEnum on Python 3.11+."""
