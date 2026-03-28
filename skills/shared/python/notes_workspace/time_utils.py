"""Time helpers."""

from __future__ import annotations

from datetime import datetime


def current_timestamp() -> str:
    """Return a timezone-aware ISO 8601 timestamp."""
    return datetime.now().astimezone().isoformat(timespec="seconds")
