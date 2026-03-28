#!/usr/bin/env python3
"""Apply agent-authored deep-distillation results and finalize source state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_package_root() -> None:
    script_path = Path(__file__).resolve()
    shared_python = script_path.parent.parent.parent / "shared" / "python"
    sys.path.insert(0, str(shared_python))


def _load_update_json(raw: str) -> dict[str, object]:
    if raw.startswith("@"):
        raw = Path(raw[1:]).read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("distillation update payload must be a JSON object")
    return payload


def main() -> int:
    _load_package_root()
    from notes_workspace.cli import emit, error_envelope, success_envelope
    from notes_workspace.distillation import apply_distillation_result
    from notes_workspace.errors import WorkspaceError
    from notes_workspace.paths import resolve_workspace_root

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-path")
    parser.add_argument("--thread-slug")
    parser.add_argument("--import-record-path")
    parser.add_argument("--import-slug")
    parser.add_argument("--update-json", required=True)
    parser.add_argument("--close-thread", action="store_true")
    parser.add_argument("--rebuild-views", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workspace-root")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        update = _load_update_json(args.update_json)
        result = apply_distillation_result(
            update=update,
            thread_path=args.thread_path,
            thread_slug=args.thread_slug,
            import_record_path=args.import_record_path,
            import_slug=args.import_slug,
            close_thread=args.close_thread,
            rebuild_views=args.rebuild_views,
            workspace_root=args.workspace_root,
            dry_run=args.dry_run,
        )
    except ValueError as exc:
        error = WorkspaceError(
            "invalid_distillation_update_json",
            str(exc),
            "Pass inline JSON or @path/to/file.json containing a JSON object.",
        )
        emit(error_envelope(root, error))
        return 2
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
