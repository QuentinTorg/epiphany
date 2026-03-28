"""Simple filesystem locks for workspace mutations."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .errors import WorkspaceError
from .paths import lock_root, resolve_workspace_root


@contextmanager
def acquire_lock(*, workspace_root: str | None = None, name: str) -> Iterator[Path]:
    root = resolve_workspace_root(workspace_root)
    locks_dir = lock_root(root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    path = locks_dir / f"{name}.lock"
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise WorkspaceError(
            "lock_conflict",
            f"Another session already holds lock {name!r}.",
            "Retry after the conflicting workflow completes.",
        ) from exc

    try:
        os.write(fd, str(os.getpid()).encode("utf-8"))
        os.close(fd)
        yield path
    finally:
        if path.exists():
            path.unlink()
