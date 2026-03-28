#!/usr/bin/env python3
"""Create the initial workspace structure and seed generated files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_package_root() -> None:
    script_path = Path(__file__).resolve()
    shared_python = script_path.parent.parent / "python"
    sys.path.insert(0, str(shared_python))


def main() -> int:
    _load_package_root()
    from notes_workspace.bootstrap import bootstrap_workspace
    from notes_workspace.cli import emit, error_envelope, success_envelope
    from notes_workspace.errors import WorkspaceError
    from notes_workspace.paths import resolve_workspace_root

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        result = bootstrap_workspace(
            workspace_root=args.workspace_root,
            force=args.force,
            dry_run=args.dry_run,
        )
    except WorkspaceError as exc:
        emit(error_envelope(root, exc))
        return 2

    emit(
        success_envelope(
            root,
            result=result,
            paths_created=result["created_dirs"],
            paths_updated=result["updated_paths"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
