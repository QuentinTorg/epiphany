#!/usr/bin/env python3
"""Return coarse retrieval candidates for agent-led query synthesis."""

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
    from notes_workspace.errors import WorkspaceError
    from notes_workspace.paths import resolve_workspace_root
    from notes_workspace.query import query_memory

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--mode", default="concise", choices=["concise", "research"])
    parser.add_argument("--topic")
    parser.add_argument("--entity")
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--source-thread")
    parser.add_argument("--source-import")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--output-file")
    parser.add_argument("--workspace-root")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        result = query_memory(
            query=args.query,
            workspace_root=args.workspace_root,
            mode=args.mode,
            topic=args.topic,
            entity=args.entity,
            date_from=args.date_from,
            date_to=args.date_to,
            source_thread=args.source_thread,
            source_import=args.source_import,
            limit=args.limit,
            offset=args.offset,
        )
    except WorkspaceError as exc:
        emit(error_envelope(root, exc))
        return 2

    if args.output_file:
        Path(args.output_file).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    emit(
        success_envelope(
            root,
            result=result,
            warnings=result["pending_warnings"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
