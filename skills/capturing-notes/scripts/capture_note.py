#!/usr/bin/env python3
"""Append a raw snippet to a thread and return current thread state."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_package_root() -> None:
    script_path = Path(__file__).resolve()
    shared_python = script_path.parent.parent.parent / "shared" / "python"
    sys.path.insert(0, str(shared_python))


def main() -> int:
    _load_package_root()
    from notes_workspace.cli import (
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
    from notes_workspace.paths import resolve_workspace_root
    from notes_workspace.threads import capture_note

    parser = build_parser(description=__doc__)
    parser.add_argument("--thread-path")
    parser.add_argument("--thread-slug")
    parser.add_argument("--thread-title")
    parser.add_argument("--stdin-body", required=True)
    parser.add_argument("--speaker")
    parser.add_argument("--timestamp")
    parser.add_argument("--create-if-missing", action="store_true")
    parser.add_argument("--workspace-root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        result = capture_note(
            thread_path=args.thread_path,
            thread_slug=args.thread_slug,
            thread_title=args.thread_title,
            stdin_body=args.stdin_body,
            speaker=args.speaker,
            timestamp=args.timestamp,
            create_if_missing=args.create_if_missing,
            workspace_root=args.workspace_root,
            dry_run=args.dry_run,
        )
    except WorkspaceError as exc:
        emit_error_diagnostic(exc)
        emit(error_envelope(root, exc))
        return exit_code_for_error(exc)

    emit_success_diagnostic("capture_note.py completed")
    emit(
        success_envelope(
            root,
            result=result,
            paths_created=result["paths_created"],
            paths_updated=result["paths_updated"],
        )
    )
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
