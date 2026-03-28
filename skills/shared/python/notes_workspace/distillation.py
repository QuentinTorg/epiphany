"""Deep-distillation apply and recovery helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .action_items import upsert_action_items
from .errors import WorkspaceError
from .frontmatter import load_markdown, write_markdown
from .locks import acquire_lock
from .paths import imports_root, relpath, resolve_workspace_root, thread_path_from_slug, thread_roots
from .threads import _load_thread, _write_thread
from .time_utils import current_timestamp
from .topics import upsert_topics
from .views import rebuild_open_threads_view, rebuild_pending_distillation_view, rebuild_static_views, rebuild_workspace_readme


def _load_update_json(raw: str) -> dict[str, Any]:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("distillation update payload must be a JSON object")
    return payload


def _resolve_import_record_path(root: Path, import_record_path: str | None, import_slug: str | None) -> Path:
    if import_record_path:
        return Path(import_record_path).resolve()
    if import_slug:
        matches = list((imports_root(root) / "records").glob(f"*/*-{import_slug}.md"))
        if not matches:
            raise WorkspaceError(
                "import_record_not_found",
                f"No import record found for slug {import_slug!r}.",
                "Pass --import-record-path or ingest the document first.",
            )
        if len(matches) > 1:
            raise WorkspaceError(
                "ambiguous_import_slug",
                f"Slug {import_slug!r} matches multiple import records.",
                "Pass --import-record-path instead of --import-slug.",
            )
        return matches[0]
    raise WorkspaceError(
        "missing_source_target",
        "One of thread or import arguments is required.",
        "Pass a thread or import target.",
    )


def _merge_unique(existing: list[str], extra: list[str]) -> list[str]:
    merged = list(existing)
    for item in extra:
        if item not in merged:
            merged.append(item)
    return merged


def _thread_closed_path(root: Path, source_path: Path, opened_at: str) -> Path:
    year = opened_at[:4]
    return thread_roots(root)["closed"] / year / source_path.name


def apply_distillation_result(
    *,
    update: dict[str, Any],
    thread_path: str | None = None,
    thread_slug: str | None = None,
    import_record_path: str | None = None,
    import_slug: str | None = None,
    close_thread: bool = False,
    rebuild_views: bool = True,
    workspace_root: str | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    root = resolve_workspace_root(workspace_root)
    source_patch = dict(update.get("source_patch", {}))
    topic_upserts = list(update.get("topic_upserts", []))
    action_item_upserts = list(update.get("action_item_upserts", []))
    views_to_rebuild = list(update.get("views_to_rebuild", []))

    is_thread = thread_path is not None or thread_slug is not None
    if is_thread:
        source_path = Path(thread_path).resolve() if thread_path else thread_path_from_slug(root, thread_slug or "")
    else:
        source_path = _resolve_import_record_path(root, import_record_path, import_slug)

    lock_name = f"thread-{source_path.stem}" if is_thread else f"import-{source_path.stem}"
    paths_created: list[str] = []
    paths_updated: list[str] = []

    with acquire_lock(workspace_root=str(root), name=lock_name):
        with acquire_lock(workspace_root=str(root), name="topics"):
            with acquire_lock(workspace_root=str(root), name="action-items"):
                if is_thread:
                    frontmatter, sections = _load_thread(source_path)
                    source_id = frontmatter["id"]
                    source_ref_key = "source_thread_refs"
                else:
                    frontmatter, body = load_markdown(source_path)
                    sections = {"body": body}
                    source_id = frontmatter["id"]
                    source_ref_key = "source_import_refs"

                now = current_timestamp()
                frontmatter["last_deep_distill_attempt_at"] = now
                if is_thread:
                    frontmatter["last_updated_at"] = now
                else:
                    frontmatter["updated_at"] = now

                topic_result = {"topic_refs": [], "paths_created": [], "paths_updated": []}
                if topic_upserts:
                    topic_result = upsert_topics(
                        workspace_root=str(root),
                        items=topic_upserts,
                        source_thread_ref=source_id if is_thread else None,
                        source_import_ref=None if is_thread else source_id,
                        dry_run=dry_run,
                    )
                    paths_created.extend(topic_result["paths_created"])
                    paths_updated.extend(topic_result["paths_updated"])

                action_item_result = {"action_item_refs": [], "paths_created": [], "paths_updated": []}
                if action_item_upserts:
                    action_item_result = upsert_action_items(
                        workspace_root=str(root),
                        items=action_item_upserts,
                        source_thread_ref=source_id if is_thread else None,
                        source_import_ref=None if is_thread else source_id,
                        dry_run=dry_run,
                    )
                    paths_created.extend(action_item_result["paths_created"])
                    paths_updated.extend(action_item_result["paths_updated"])

                if topic_result["topic_refs"]:
                    existing = frontmatter.get("primary_topic_refs", [])
                    frontmatter["primary_topic_refs"] = _merge_unique(existing, list(topic_result["topic_refs"]))
                if action_item_result["action_item_refs"]:
                    existing = frontmatter.get("action_item_refs", [])
                    frontmatter["action_item_refs"] = _merge_unique(existing, list(action_item_result["action_item_refs"]))

                for key, value in source_patch.items():
                    frontmatter[key] = value

                if frontmatter.get("distillation_state") == "complete":
                    frontmatter["pending_reason"] = source_patch.get("pending_reason", [])
                    frontmatter["deep_distilled_at"] = source_patch.get("deep_distilled_at", now)
                elif "pending_reason" in source_patch:
                    frontmatter["pending_reason"] = source_patch["pending_reason"]

                final_source_path = source_path
                if is_thread and close_thread and frontmatter.get("distillation_state") == "complete":
                    frontmatter["thread_status"] = "closed"
                    frontmatter["closed_at"] = source_patch.get("closed_at", now)
                    final_source_path = _thread_closed_path(root, source_path, frontmatter["opened_at"])

                source_relpath = relpath(final_source_path, root)
                if not dry_run:
                    if is_thread:
                        _write_thread(final_source_path, frontmatter, sections)
                    else:
                        write_markdown(final_source_path, frontmatter, sections["body"])
                    if final_source_path != source_path and source_path.exists():
                        source_path.unlink()
                    paths_updated.append(source_relpath)

                    if rebuild_views:
                        with acquire_lock(workspace_root=str(root), name="views"):
                            paths_updated.extend(rebuild_static_views(root))
                            paths_updated.extend(rebuild_open_threads_view(root))
                            paths_updated.extend(rebuild_pending_distillation_view(root))
                            paths_updated.extend(rebuild_workspace_readme(root))
                    elif views_to_rebuild:
                        with acquire_lock(workspace_root=str(root), name="views"):
                            if "static" in views_to_rebuild:
                                paths_updated.extend(rebuild_static_views(root))
                            if "open-threads" in views_to_rebuild:
                                paths_updated.extend(rebuild_open_threads_view(root))
                            if "pending-distillation" in views_to_rebuild:
                                paths_updated.extend(rebuild_pending_distillation_view(root))
                            if "workspace-readme" in views_to_rebuild:
                                paths_updated.extend(rebuild_workspace_readme(root))
                else:
                    paths_updated.append(source_relpath)

    return {
        "source_path": source_relpath,
        "source_id": source_id,
        "topic_refs": topic_result["topic_refs"],
        "action_item_refs": action_item_result["action_item_refs"],
        "distillation_state": frontmatter.get("distillation_state"),
        "thread_status": frontmatter.get("thread_status") if is_thread else None,
        "paths_created": paths_created,
        "paths_updated": paths_updated,
    }


def resume_pending(
    *,
    workspace_root: str | None = None,
    thread_slug: str | None = None,
    import_slug: str | None = None,
    all_items: bool = False,
) -> dict[str, object]:
    root = resolve_workspace_root(workspace_root)
    items: list[dict[str, str]] = []

    for path in sorted((root / "memory" / "threads").glob("*/*/*.md")):
        frontmatter, _ = load_markdown(path)
        if frontmatter.get("doc_type") != "thread":
            continue
        if thread_slug and frontmatter.get("slug") != thread_slug:
            continue
        if not all_items and thread_slug is None and import_slug is None and frontmatter.get("distillation_state") != "pending":
            continue
        if frontmatter.get("distillation_state") == "pending":
            items.append(
                {
                    "source_type": "thread",
                    "id": frontmatter["id"],
                    "title": frontmatter["title"],
                    "path": relpath(path, root),
                    "pending_reason": ", ".join(frontmatter.get("pending_reason", [])) or "pending",
                }
            )

    for path in sorted((imports_root(root) / "records").glob("*/*.md")):
        frontmatter, _ = load_markdown(path)
        if frontmatter.get("doc_type") != "import-record":
            continue
        if import_slug and frontmatter.get("slug") != import_slug:
            continue
        if not all_items and thread_slug is None and import_slug is None and frontmatter.get("distillation_state") != "pending":
            continue
        if frontmatter.get("distillation_state") == "pending":
            items.append(
                {
                    "source_type": "import",
                    "id": frontmatter["id"],
                    "title": frontmatter["title"],
                    "path": relpath(path, root),
                    "pending_reason": ", ".join(frontmatter.get("pending_reason", [])) or "pending",
                }
            )

    return {"items": items, "total": len(items)}
