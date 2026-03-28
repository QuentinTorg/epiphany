#!/usr/bin/env python3
"""Refresh thread metadata and mechanical views after direct agent edits.

This wrapper does not perform semantic summarization or topic reconciliation.
It only updates structural metadata and generated views that can be derived
mechanically from the already-edited thread and any explicit action-item payload.
"""

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
    from notes_workspace.cli import emit, error_envelope, success_envelope
    from notes_workspace.errors import WorkspaceError
    from notes_workspace.paths import resolve_workspace_root
    from notes_workspace.threads import sync_thread_state

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-path", required=True)
    parser.add_argument("--canonical-action-items-json")
    parser.add_argument("--workspace-root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = resolve_workspace_root(args.workspace_root)
    try:
        canonical_action_items = _load_action_items(args.canonical_action_items_json)
        result = sync_thread_state(
            thread_path=args.thread_path,
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
        emit(error_envelope(root, error))
        return 2
    except WorkspaceError as exc:
        emit(error_envelope(root, exc))
        return 2

    emit(
        success_envelope(
            root,
            result=result,
            paths_updated=result["paths_updated"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
