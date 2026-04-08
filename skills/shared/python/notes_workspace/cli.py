"""CLI helpers for wrapper scripts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .errors import WorkspaceError

EXIT_OK = 0
EXIT_INVALID_ARGUMENTS = 2
EXIT_WORKSPACE_ERROR = 3
EXIT_LOCK_CONFLICT = 4

EXIT_CODE_HELP = """Exit codes:
  0  Success
  2  Invalid arguments or malformed wrapper JSON input
  3  Workspace operation failed
  4  Lock conflict; another session already holds the relevant workspace lock
"""


def build_parser(*, description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXIT_CODE_HELP,
    )


def exit_code_for_error(error: WorkspaceError) -> int:
    if error.code == "lock_conflict":
        return EXIT_LOCK_CONFLICT
    return EXIT_WORKSPACE_ERROR


def emit_success_diagnostic(message: str, *, warnings: list[str] | None = None) -> None:
    print(f"OK: {message}", file=sys.stderr)
    for warning in warnings or []:
        print(f"WARNING: {warning}", file=sys.stderr)


def emit_error_diagnostic(error: WorkspaceError) -> None:
    print(f"ERROR [{error.code}]: {error.message}", file=sys.stderr)
    if error.hint:
        print(f"HINT: {error.hint}", file=sys.stderr)


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
