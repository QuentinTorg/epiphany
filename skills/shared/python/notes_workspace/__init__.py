"""Shared implementation for the Agentic Notes Workspace."""

from .bootstrap import bootstrap_workspace
from .threads import apply_thread_update, capture_note, get_thread_status

__all__ = [
    "apply_thread_update",
    "bootstrap_workspace",
    "capture_note",
    "get_thread_status",
]
