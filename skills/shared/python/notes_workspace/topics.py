"""Canonical topic storage and listing."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .documents import parse_topic_body, preview_from_text, render_topic_body
from .errors import WorkspaceError
from .frontmatter import load_markdown, write_markdown
from .paths import TOPIC_TYPES, relpath, resolve_workspace_root, topics_root
from .time_utils import current_timestamp

DEFAULT_ENTITY_BY_TYPE = {
    "people": True,
    "projects": True,
    "customers": True,
    "systems": True,
    "classes": True,
    "products": True,
    "documents": True,
    "places": True,
    "concepts": False,
    "custom": False,
    "other": False,
}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "topic"


def custom_type_dir_name(custom_type: str) -> str:
    return _slugify(custom_type)


def _topic_path(
    workspace_root: Path,
    *,
    topic_type: str,
    slug: str,
    custom_type: str | None = None,
) -> Path:
    if topic_type == "custom":
        if not custom_type:
            raise WorkspaceError(
                "missing_custom_type",
                "Custom topics require a custom_type value.",
                "Provide a custom_type in the topic upsert payload.",
            )
        return topics_root(workspace_root) / "custom" / custom_type_dir_name(custom_type) / f"{slug}.md"
    return topics_root(workspace_root) / topic_type / f"{slug}.md"


def _find_by_id(workspace_root: Path, topic_id: str) -> Path | None:
    for path in topics_root(workspace_root).rglob("*.md"):
        if path.name == "index.md":
            continue
        frontmatter, _ = load_markdown(path)
        if frontmatter.get("id") == topic_id:
            return path
    return None


def _find_by_type_slug(
    workspace_root: Path,
    *,
    topic_type: str,
    slug: str,
    custom_type: str | None = None,
) -> Path | None:
    path = _topic_path(workspace_root, topic_type=topic_type, slug=slug, custom_type=custom_type)
    return path if path.exists() else None


def _load_existing(path: Path) -> tuple[dict[str, Any], dict[str, str]]:
    frontmatter, body = load_markdown(path)
    return frontmatter, parse_topic_body(body)


def _merge_unique(existing: list[str], extra: list[str]) -> list[str]:
    merged = list(existing)
    for item in extra:
        if item not in merged:
            merged.append(item)
    return merged


def upsert_topics(
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
    topic_refs: list[str] = []

    for item in items:
        topic_type = item["type"]
        if topic_type not in TOPIC_TYPES:
            raise WorkspaceError(
                "invalid_topic_type",
                f"Unsupported topic type {topic_type!r}.",
                f"Use one of: {', '.join(TOPIC_TYPES)}.",
            )

        title = item["title"].strip()
        slug = item.get("slug") or _slugify(title)
        custom_type = item.get("custom_type")
        topic_id = item.get("id") or f"top-{topic_type}-{slug}"
        now = current_timestamp()

        existing_path = None
        if item.get("id"):
            existing_path = _find_by_id(root, item["id"])
        if existing_path is None:
            existing_path = _find_by_type_slug(root, topic_type=topic_type, slug=slug, custom_type=custom_type)

        if existing_path:
            frontmatter, body = _load_existing(existing_path)
            created_at = frontmatter["created_at"]
            topic_id = frontmatter["id"]
            manual_notes = body.get("manual_notes", "")
        else:
            frontmatter = {}
            manual_notes = ""
            created_at = item.get("created_at") or now

        aliases = _merge_unique(frontmatter.get("aliases", []), list(item.get("aliases", [])))
        related_topic_refs = _merge_unique(frontmatter.get("related_topic_refs", []), list(item.get("related_topic_refs", [])))
        source_thread_refs = _merge_unique(frontmatter.get("source_thread_refs", []), [source_thread_ref] if source_thread_ref else [])
        source_thread_refs = _merge_unique(source_thread_refs, list(item.get("source_thread_refs", [])))
        source_import_refs = _merge_unique(frontmatter.get("source_import_refs", []), [source_import_ref] if source_import_ref else [])
        source_import_refs = _merge_unique(source_import_refs, list(item.get("source_import_refs", [])))
        action_item_refs = _merge_unique(frontmatter.get("action_item_refs", []), list(item.get("action_item_refs", [])))

        topic_path = _topic_path(root, topic_type=topic_type, slug=slug, custom_type=custom_type)
        new_frontmatter = {
            "doc_type": "topic",
            "id": topic_id,
            "title": title,
            "slug": slug,
            "preview": preview_from_text(item["summary_markdown"], f"Topic: {title}")[:240],
            "type": topic_type,
            "custom_type": custom_type if topic_type == "custom" else None,
            "entity": item.get("entity", DEFAULT_ENTITY_BY_TYPE[topic_type]),
            "status": item.get("status", "active"),
            "created_at": created_at,
            "updated_at": now,
            "summary_updated_at": item.get("summary_updated_at", now),
            "freshness": item.get("freshness", "current"),
            "aliases": aliases,
            "related_topic_refs": related_topic_refs,
            "source_thread_refs": source_thread_refs,
            "source_import_refs": source_import_refs,
            "action_item_refs": action_item_refs,
        }
        body = render_topic_body(
            title=title,
            summary=item["summary_markdown"],
            current_understanding=item["current_understanding_markdown"],
            key_facts=item["key_facts_markdown"],
            related_topics=item["related_topics_markdown"],
            recent_evidence=item["recent_evidence_markdown"],
            change_history=item["change_history_markdown"],
            manual_notes=manual_notes,
        )

        topic_refs.append(topic_id)
        if dry_run:
            if existing_path is None:
                paths_created.append(relpath(topic_path, root))
            paths_updated.append(relpath(topic_path, root))
            continue

        write_markdown(topic_path, new_frontmatter, body)
        if existing_path and existing_path != topic_path and existing_path.exists():
            existing_path.unlink()
        if existing_path is None:
            paths_created.append(relpath(topic_path, root))
        paths_updated.append(relpath(topic_path, root))

    return {
        "topic_refs": topic_refs,
        "paths_created": paths_created,
        "paths_updated": paths_updated,
    }


def list_topics(
    *,
    workspace_root: str | None = None,
    topic_type: str | None = None,
) -> list[dict[str, Any]]:
    root = resolve_workspace_root(workspace_root)
    results: list[dict[str, Any]] = []
    for path in sorted(topics_root(root).rglob("*.md")):
        if path.name == "index.md":
            continue
        frontmatter, body = load_markdown(path)
        if frontmatter.get("doc_type") != "topic":
            continue
        if topic_type and frontmatter.get("type") != topic_type:
            continue
        parsed = parse_topic_body(body)
        results.append(
            {
                "path": relpath(path, root),
                "id": frontmatter["id"],
                "title": frontmatter["title"],
                "slug": frontmatter["slug"],
                "type": frontmatter["type"],
                "custom_type": frontmatter.get("custom_type"),
                "entity": frontmatter["entity"],
                "status": frontmatter["status"],
                "freshness": frontmatter["freshness"],
                "preview": frontmatter["preview"],
                "updated_at": frontmatter["updated_at"],
                "summary": parsed["summary"],
                "current_understanding": parsed["current_understanding"],
            }
        )
    return results
