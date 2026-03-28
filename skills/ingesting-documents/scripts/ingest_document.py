#!/usr/bin/env python3
"""Register a source document, normalize it to text, and create an import record."""

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
    from notes_workspace.imports import ingest_document
    from notes_workspace.paths import resolve_workspace_root

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-path", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug")
    parser.add_argument("--imported-at")
    parser.add_argument("--workspace-root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        result = ingest_document(
            source_path=args.source_path,
            title=args.title,
            slug=args.slug,
            imported_at=args.imported_at,
            workspace_root=args.workspace_root,
            dry_run=args.dry_run,
        )
    except WorkspaceError as exc:
        emit(error_envelope(root, exc))
        return 2

    emit(
        success_envelope(
            root,
            result=result,
            paths_created=result["paths_created"],
            paths_updated=result["paths_updated"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
