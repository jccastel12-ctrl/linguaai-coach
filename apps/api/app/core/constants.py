"""Shared domain constants."""

from typing import Literal

CEFR_LEVELS: tuple[str, ...] = ("A1", "A2", "B1", "B2", "C1", "C2")
CefrLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]

PROGRESS_STATUSES: tuple[str, ...] = ("not_started", "in_progress", "completed")
ProgressStatus = Literal["not_started", "in_progress", "completed"]

# Languages supported at launch (ISO 639-1).
SUPPORTED_LANGUAGES: tuple[dict[str, str], ...] = (
    {"code": "es", "name": "Spanish", "native_name": "Español"},
    {"code": "en", "name": "English", "native_name": "English"},
    {"code": "sr", "name": "Serbian", "native_name": "Српски / Srpski"},
)


def sql_in(values: tuple[str, ...]) -> str:
    """Render a tuple as a SQL IN list for CHECK constraints."""
    return "(" + ", ".join(f"'{v}'" for v in values) + ")"
