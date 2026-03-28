"""Canonical action-item storage and filtering."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .documents import parse_action_item_body, preview_from_text, render_action_item_body
from .errors import WorkspaceError
from .frontmatter import load_markdown, write_markdown
from .paths import action_items_root, relpath, resolve_workspace_root
from .time_utils import current_timestamp

TERMINAL_STATUSES = {"done", "cancelled", "resolved"}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def _item_year(created_at: str) -> str:
    return created_at[:4]


def _action_item_path(workspace_root: Path, *, created_at: str, kind: str, slug: str, status: str) -> Path:
    base = action_items_root(workspace_root)
    filename = f"{created_at[:10]}-{kind}-{slug}.md"
    if status in TERMINAL_STATUSES:
        return base / "closed" / _item_year(created_at) / filename
    return base / "open" / _item_year(created_at) / filename


def _find_by_id(workspace_root: Path, item_id: str) -> Path | None:
    for path in action_items_root(workspace_root).glob("*/*/*.md"):
        frontmatter, _ = load_markdown(path)
        if frontmatter.get("id") == item_id:
            return path
    return None


def _find_by_kind_slug(workspace_root: Path, kind: str, slug: str) -> Path | None:
    matches: list[Path] = []
    for path in action_items_root(workspace_root).glob("*/*/*.md"):
        frontmatter, _ = load_markdown(path)
        if frontmatter.get("kind") == kind and frontmatter.get("slug") == slug:
            matches.append(path)
    if len(matches) > 1:
        raise WorkspaceError(
            "ambiguous_action_item",
            f"Multiple action items match kind={kind!r} and slug={slug!r}.",
            "Provide an explicit action-item id in the canonical action item payload.",
        )
    return matches[0] if matches else None


def _load_existing(path: Path) -> tuple[dict[str, Any], dict[str, str]]:
    frontmatter, body = load_markdown(path)
    return frontmatter, parse_action_item_body(body)


def _merge_unique(existing: list[str], extra: list[str]) -> list[str]:
    merged = list(existing)
    for item in extra:
        if item not in merged:
            merged.append(item)
    return merged


def upsert_action_items(
    *,
    workspace_root: str | None = None,
    items: list[dict[str, Any]],
    source_thread_ref: str | None = None,
    source_import_ref: str | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    root = resolve_workspace_root(workspace_root)
    paths_created: list[str] = []
    paths_updated: list[str] = []
    action_item_refs: list[str] = []

    for item in items:
        kind = item["kind"]
        if kind not in {"task", "question"}:
            raise WorkspaceError(
                "invalid_action_item_kind",
                f"Unsupported action-item kind {kind!r}.",
                "Use either 'task' or 'question'.",
            )
        title = item["title"].strip()
        slug = item.get("slug") or _slugify(title)
        status = item.get("status", "open")
        created_at = item.get("created_at") or current_timestamp()
        updated_at = current_timestamp()
        item_id = item.get("id") or f"act-{created_at[:10]}-{kind}-{slug}"

        existing_path = None
        if item.get("id"):
            existing_path = _find_by_id(root, item["id"])
        if existing_path is None:
            existing_path = _find_by_kind_slug(root, kind, slug)

        if existing_path:
            frontmatter, body = _load_existing(existing_path)
            created_at = frontmatter["created_at"]
            item_id = frontmatter["id"]
            manual_notes = body.get("manual_notes", "")
        else:
            frontmatter = {}
            manual_notes = ""

        owner_topic_refs = _merge_unique(frontmatter.get("owner_topic_refs", []), list(item.get("owner_topic_refs", [])))
        linked_topic_refs = _merge_unique(frontmatter.get("linked_topic_refs", []), list(item.get("linked_topic_refs", [])))
        source_thread_refs = _merge_unique(frontmatter.get("source_thread_refs", []), [source_thread_ref] if source_thread_ref else [])
        source_thread_refs = _merge_unique(source_thread_refs, list(item.get("source_thread_refs", [])))
        source_import_refs = _merge_unique(frontmatter.get("source_import_refs", []), [source_import_ref] if source_import_ref else [])
        source_import_refs = _merge_unique(source_import_refs, list(item.get("source_import_refs", [])))

        new_frontmatter = {
            "doc_type": "action-item",
            "id": item_id,
            "kind": kind,
            "title": title,
            "slug": slug,
            "preview": preview_from_text(item["summary_markdown"], f"{kind.title()} item: {title}")[:240],
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at,
            "closed_at": updated_at if status in TERMINAL_STATUSES else None,
            "due_at": item.get("due_at"),
            "priority": item.get("priority", "medium"),
            "confidence": item.get("confidence", "explicit"),
            "owner_topic_refs": owner_topic_refs,
            "linked_topic_refs": linked_topic_refs,
            "source_thread_refs": source_thread_refs,
            "source_import_refs": source_import_refs,
        }
        body = render_action_item_body(
            title=title,
            summary=item["summary_markdown"],
            current_state=item["current_state_markdown"],
            evidence=item["evidence_markdown"],
            resolution_history=item.get("resolution_history_markdown", "No resolution history yet."),
            manual_notes=manual_notes,
        )

        path = _action_item_path(root, created_at=created_at, kind=kind, slug=slug, status=status)
        action_item_refs.append(item_id)
        if dry_run:
            if existing_path is None:
                paths_created.append(relpath(path, root))
            else:
                paths_updated.append(relpath(path, root))
            continue

        write_markdown(path, new_frontmatter, body)
        if existing_path and existing_path != path and existing_path.exists():
            existing_path.unlink()
        if existing_path is None:
            paths_created.append(relpath(path, root))
        paths_updated.append(relpath(path, root))

    return {
        "action_item_refs": action_item_refs,
        "paths_created": paths_created,
        "paths_updated": paths_updated,
    }


def list_action_items(
    *,
    workspace_root: str | None = None,
    kind: str = "all",
    status: str | None = None,
    owner: str | None = None,
    topic: str | None = None,
    entity: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    source_thread: str | None = None,
    source_import: str | None = None,
    include_closed: bool = False,
    limit: int | None = None,
    offset: int = 0,
) -> dict[str, object]:
    root = resolve_workspace_root(workspace_root)
    matches: list[dict[str, Any]] = []
    glob_patterns = ["open/*/*.md", "closed/*/*.md"] if include_closed else ["open/*/*.md"]

    for pattern in glob_patterns:
        for path in sorted(action_items_root(root).glob(pattern)):
            frontmatter, body = load_markdown(path)
            if kind != "all" and frontmatter.get("kind") != kind:
                continue
            if status and frontmatter.get("status") != status:
                continue
            if owner and owner not in frontmatter.get("owner_topic_refs", []):
                continue
            if topic and topic not in frontmatter.get("linked_topic_refs", []):
                continue
            if entity and entity not in (frontmatter.get("linked_topic_refs", []) + frontmatter.get("owner_topic_refs", [])):
                continue
            if source_thread and source_thread not in frontmatter.get("source_thread_refs", []):
                continue
            if source_import and source_import not in frontmatter.get("source_import_refs", []):
                continue
            updated_at = frontmatter.get("updated_at")
            if date_from and updated_at < date_from:
                continue
            if date_to and updated_at > date_to:
                continue
            parsed_body = parse_action_item_body(body)
            matches.append(
                {
                    "path": relpath(path, root),
                    "id": frontmatter["id"],
                    "kind": frontmatter["kind"],
                    "title": frontmatter["title"],
                    "preview": frontmatter["preview"],
                    "status": frontmatter["status"],
                    "priority": frontmatter["priority"],
                    "confidence": frontmatter["confidence"],
                    "due_at": frontmatter["due_at"],
                    "owner_topic_refs": frontmatter.get("owner_topic_refs", []),
                    "linked_topic_refs": frontmatter.get("linked_topic_refs", []),
                    "source_thread_refs": frontmatter.get("source_thread_refs", []),
                    "source_import_refs": frontmatter.get("source_import_refs", []),
                    "summary": parsed_body["summary"],
                    "current_state": parsed_body["current_state"],
                }
            )

    matches.sort(key=lambda item: (item["status"], item["title"]))
    sliced = matches[offset:]
    if limit is not None:
        sliced = sliced[:limit]
    return {
        "items": sliced,
        "total": len(matches),
        "offset": offset,
        "limit": limit,
    }
