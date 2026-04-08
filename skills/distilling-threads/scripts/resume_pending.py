#!/usr/bin/env python3
"""List pending deep-distillation records for agent-driven recovery."""

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
    from notes_workspace.distillation import resume_pending
    from notes_workspace.errors import WorkspaceError
    from notes_workspace.paths import resolve_workspace_root

    parser = build_parser(description=__doc__)
    parser.add_argument("--thread-slug")
    parser.add_argument("--import-slug")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--workspace-root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        result = resume_pending(
            workspace_root=args.workspace_root,
            thread_slug=args.thread_slug,
            import_slug=args.import_slug,
            all_items=args.all,
            dry_run=args.dry_run,
        )
    except WorkspaceError as exc:
        emit_error_diagnostic(exc)
        emit(error_envelope(root, exc))
        return exit_code_for_error(exc)

    emit_success_diagnostic("resume_pending.py completed")
    emit(success_envelope(root, result=result))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
