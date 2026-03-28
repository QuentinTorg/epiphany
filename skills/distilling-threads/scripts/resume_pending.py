#!/usr/bin/env python3
"""List pending deep-distillation records for agent-driven recovery."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_package_root() -> None:
    script_path = Path(__file__).resolve()
    shared_python = script_path.parent.parent.parent / "shared" / "python"
    sys.path.insert(0, str(shared_python))


def main() -> int:
    _load_package_root()
    from notes_workspace.cli import emit, error_envelope, success_envelope
    from notes_workspace.distillation import resume_pending
    from notes_workspace.errors import WorkspaceError
    from notes_workspace.paths import resolve_workspace_root

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-slug")
    parser.add_argument("--import-slug")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--output-file")
    parser.add_argument("--workspace-root")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        result = resume_pending(
            workspace_root=args.workspace_root,
            thread_slug=args.thread_slug,
            import_slug=args.import_slug,
            all_items=args.all,
        )
    except WorkspaceError as exc:
        emit(error_envelope(root, exc))
        return 2

    if args.output_file:
        Path(args.output_file).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    emit(success_envelope(root, result=result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
