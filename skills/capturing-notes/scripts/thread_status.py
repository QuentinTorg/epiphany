#!/usr/bin/env python3
"""Show the current state of a thread."""

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
    from notes_workspace.cli import emit, error_envelope, success_envelope
    from notes_workspace.errors import WorkspaceError
    from notes_workspace.paths import resolve_workspace_root
    from notes_workspace.threads import get_thread_status

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-path")
    parser.add_argument("--thread-slug")
    parser.add_argument("--workspace-root")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        result = get_thread_status(
            thread_path=args.thread_path,
            thread_slug=args.thread_slug,
            workspace_root=args.workspace_root,
        )
    except WorkspaceError as exc:
        emit(error_envelope(root, exc))
        return 2

    emit(success_envelope(root, result=result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
