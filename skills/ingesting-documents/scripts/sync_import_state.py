#!/usr/bin/env python3
"""Refresh import metadata and mechanical views after direct agent edits."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_package_root() -> None:
    script_path = Path(__file__).resolve()
    shared_python = script_path.parent.parent.parent / "shared" / "python"
    sys.path.insert(0, str(shared_python))


def _load_action_items(raw: str | None) -> list[dict[str, object]] | None:
    if raw is None:
        return None
    if raw.startswith("@"):
        raw = Path(raw[1:]).read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, list):
        raise ValueError("canonical action items payload must be a JSON list")
    return payload


def main() -> int:
    _load_package_root()
    from notes_workspace.cli import (
        EXIT_INVALID_ARGUMENTS,
        EXIT_OK,
        build_parser,
        emit,
        emit_error_diagnostic,
        emit_success_diagnostic,
        error_envelope,
        exit_code_for_error,
        success_envelope,
    )
    from notes_workspace.errors import WorkspaceError
    from notes_workspace.imports import sync_import_state
    from notes_workspace.paths import resolve_workspace_root

    parser = build_parser(description=__doc__)
    parser.add_argument("--import-record-path", required=True)
    parser.add_argument("--canonical-action-items-json")
    parser.add_argument("--workspace-root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        canonical_action_items = _load_action_items(args.canonical_action_items_json)
        result = sync_import_state(
            import_record_path=args.import_record_path,
            workspace_root=args.workspace_root,
            canonical_action_items=canonical_action_items,
            dry_run=args.dry_run,
        )
    except ValueError as exc:
        error = WorkspaceError(
            "invalid_canonical_action_items_json",
            str(exc),
            "Pass inline JSON or @path/to/file.json containing a JSON list.",
        )
        emit_error_diagnostic(error)
        emit(error_envelope(root, error))
        return EXIT_INVALID_ARGUMENTS
    except WorkspaceError as exc:
        emit_error_diagnostic(exc)
        emit(error_envelope(root, exc))
        return exit_code_for_error(exc)

    emit_success_diagnostic("sync_import_state.py completed")
    emit(
        success_envelope(
            root,
            result=result,
            paths_updated=result["paths_updated"],
        )
    )
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
