"""CLI helpers for wrapper scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import WorkspaceError


def success_envelope(
    workspace_root: Path,
    *,
    result: dict[str, Any],
    paths_created: list[str] | None = None,
    paths_updated: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "workspace_root": str(workspace_root),
        "warnings": warnings or [],
        "paths_created": paths_created or [],
        "paths_updated": paths_updated or [],
        "result": result,
        "error": None,
    }


def error_envelope(workspace_root: Path | None, error: WorkspaceError) -> dict[str, Any]:
    return {
        "ok": False,
        "workspace_root": str(workspace_root) if workspace_root else None,
        "warnings": [],
        "paths_created": [],
        "paths_updated": [],
        "result": None,
        "error": {
            "code": error.code,
            "message": error.message,
            "hint": error.hint,
        },
    }


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))
