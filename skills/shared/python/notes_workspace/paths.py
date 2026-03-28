"""Path and workspace layout helpers."""

from __future__ import annotations

import os
from pathlib import Path

from .errors import WorkspaceError

TOPIC_TYPES = [
    "people",
    "projects",
    "customers",
    "systems",
    "classes",
    "products",
    "documents",
    "places",
    "concepts",
    "custom",
    "other",
]


def resolve_workspace_root(workspace_root: str | None = None) -> Path:
    return Path(workspace_root or os.getcwd()).resolve()


def memory_root(workspace_root: Path) -> Path:
    return workspace_root / "memory"


def thread_roots(workspace_root: Path) -> dict[str, Path]:
    root = memory_root(workspace_root) / "threads"
    return {"open": root / "open", "closed": root / "closed"}


def view_root(workspace_root: Path) -> Path:
    return memory_root(workspace_root) / "views"


def imports_root(workspace_root: Path) -> Path:
    return memory_root(workspace_root) / "imports"


def topics_root(workspace_root: Path) -> Path:
    return memory_root(workspace_root) / "topics"


def action_items_root(workspace_root: Path) -> Path:
    return memory_root(workspace_root) / "action-items"


def runtime_root(workspace_root: Path) -> Path:
    return workspace_root / ".notes-runtime"


def lock_root(workspace_root: Path) -> Path:
    return runtime_root(workspace_root) / "locks"


def relpath(path: Path, workspace_root: Path) -> str:
    return str(path.relative_to(workspace_root))


def is_git_workspace(workspace_root: Path) -> bool:
    return (workspace_root / ".git").exists()


def ensure_workspace_directories(workspace_root: Path) -> list[Path]:
    created: list[Path] = []
    paths = [
        lock_root(workspace_root),
        thread_roots(workspace_root)["open"],
        thread_roots(workspace_root)["closed"],
        imports_root(workspace_root) / "files",
        imports_root(workspace_root) / "text",
        imports_root(workspace_root) / "records",
        action_items_root(workspace_root) / "open",
        action_items_root(workspace_root) / "closed",
        view_root(workspace_root),
        topics_root(workspace_root),
        topics_root(workspace_root) / "custom",
    ]
    paths.extend(topics_root(workspace_root) / topic_type for topic_type in TOPIC_TYPES if topic_type != "custom")

    for path in paths:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)
    return created


def ensure_gitignore(workspace_root: Path) -> list[Path]:
    if not is_git_workspace(workspace_root):
        return []
    gitignore = workspace_root / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
    wanted = [".notes-runtime/"]
    changed = False
    for item in wanted:
        if item not in existing:
            existing.append(item)
            changed = True
    if changed:
        gitignore.write_text("\n".join(existing).rstrip() + "\n", encoding="utf-8")
        return [gitignore]
    return []


def parse_year_from_timestamp(timestamp: str) -> str:
    return timestamp[:4]


def thread_path_from_slug(workspace_root: Path, slug: str) -> Path:
    matches = list(memory_root(workspace_root).glob(f"threads/*/*/*-{slug}.md"))
    if not matches:
        raise WorkspaceError(
            "thread_not_found",
            f"No thread found for slug {slug!r}.",
            "Create the thread first or pass --create-if-missing with a title.",
        )
    if len(matches) > 1:
        raise WorkspaceError(
            "ambiguous_slug",
            f"Slug {slug!r} matches multiple thread files.",
            "Pass --thread-path instead of --thread-slug.",
        )
    return matches[0]
