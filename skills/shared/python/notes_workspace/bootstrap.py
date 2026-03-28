"""Workspace bootstrap operations."""

from __future__ import annotations

from pathlib import Path

from .paths import ensure_gitignore, ensure_workspace_directories, relpath, resolve_workspace_root
from .views import rebuild_all_views


def bootstrap_workspace(*, workspace_root: str | None = None, force: bool = False, dry_run: bool = False) -> dict[str, object]:
    del force  # Reserved for later stricter behavior.
    root = resolve_workspace_root(workspace_root)
    created_dirs = ensure_workspace_directories(root) if not dry_run else []
    updated_paths = rebuild_all_views(root) if not dry_run else []
    gitignore_paths = ensure_gitignore(root) if not dry_run else []
    return {
        "workspace_root": str(root),
        "created_dirs": [relpath(path, root) for path in created_dirs],
        "updated_paths": updated_paths + [relpath(path, root) for path in gitignore_paths],
    }
