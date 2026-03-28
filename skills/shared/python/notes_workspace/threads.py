"""Thread capture and thread-local sync operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .action_items import upsert_action_items
from .documents import next_snippet_id, parse_thread_body, preview_from_text, render_snippet, render_thread_body
from .errors import WorkspaceError
from .frontmatter import load_markdown, write_markdown
from .paths import memory_root, parse_year_from_timestamp, relpath, resolve_workspace_root, thread_path_from_slug, thread_roots
from .time_utils import current_timestamp
from .views import rebuild_open_threads_view, rebuild_pending_distillation_view, rebuild_static_views, rebuild_workspace_readme


def _thread_placeholders() -> dict[str, str]:
    return {
        "summary": "Summary pending. [sources: ]",
        "open_questions": "No open questions yet.",
        "candidate_action_items": "No candidate action items yet.",
        "distillation_notes": "Awaiting lightweight distillation.",
    }


def _new_thread_frontmatter(*, slug: str, title: str, timestamp: str) -> dict[str, Any]:
    return {
        "doc_type": "thread",
        "id": f"thr-{timestamp[:10]}-{slug}",
        "title": title,
        "slug": slug,
        "preview": "Open thread with captured notes; summary pending.",
        "thread_status": "open",
        "source_type": "conversation",
        "opened_at": timestamp,
        "last_updated_at": timestamp,
        "closed_at": None,
        "distillation_state": "pending",
        "light_distilled_at": None,
        "deep_distilled_at": None,
        "last_deep_distill_attempt_at": None,
        "pending_reason": ["new-snippets"],
        "primary_topic_refs": [],
        "primary_entity_refs": [],
        "action_item_refs": [],
    }


def _thread_path_for_new(workspace_root: Path, timestamp: str, slug: str) -> Path:
    year = parse_year_from_timestamp(timestamp)
    return thread_roots(workspace_root)["open"] / year / f"{timestamp[:10]}-{slug}.md"


def _load_thread(path: Path) -> tuple[dict[str, Any], dict[str, str]]:
    frontmatter, body = load_markdown(path)
    return frontmatter, parse_thread_body(body)


def _write_thread(path: Path, frontmatter: dict[str, Any], sections: dict[str, str]) -> None:
    body = render_thread_body(
        title=frontmatter["title"],
        summary=sections["summary"],
        open_questions=sections["open_questions"],
        candidate_action_items=sections["candidate_action_items"],
        distillation_notes=sections["distillation_notes"],
        snippets=sections["snippets"],
    )
    write_markdown(path, frontmatter, body)


def capture_note(
    *,
    thread_path: str | None = None,
    thread_slug: str | None = None,
    thread_title: str | None = None,
    stdin_body: str,
    speaker: str | None = None,
    timestamp: str | None = None,
    create_if_missing: bool = False,
    workspace_root: str | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    root = resolve_workspace_root(workspace_root)
    ts = timestamp or current_timestamp()

    if not thread_path and not thread_slug:
        raise WorkspaceError(
            "missing_thread_target",
            "One of --thread-path or --thread-slug is required.",
            "Pass a thread path or slug, and use --create-if-missing when creating a new thread.",
        )

    if thread_path:
        path = Path(thread_path).resolve()
    else:
        try:
            path = thread_path_from_slug(root, thread_slug or "")
        except WorkspaceError:
            if not create_if_missing:
                raise
            if not thread_title:
                raise WorkspaceError(
                    "missing_thread_title",
                    "--thread-title is required when --create-if-missing is used.",
                    "Pass a human-readable title for the new thread.",
                )
            path = _thread_path_for_new(root, ts, thread_slug or "")

    created = not path.exists()
    if created and not create_if_missing:
        raise WorkspaceError(
            "thread_not_found",
            f"Thread path {path} does not exist.",
            "Use --create-if-missing to create a new thread.",
        )

    if created:
        frontmatter = _new_thread_frontmatter(slug=thread_slug or path.stem[11:], title=thread_title or path.stem, timestamp=ts)
        sections = {
            **_thread_placeholders(),
            "snippets": "",
        }
    else:
        frontmatter, sections = _load_thread(path)

    snippet_id = next_snippet_id(sections["snippets"])
    snippet = render_snippet(snippet_id=snippet_id, timestamp=ts, body=stdin_body, speaker=speaker)
    sections["snippets"] = f"{sections['snippets'].rstrip()}\n\n{snippet}".strip() if sections["snippets"].strip() else snippet

    frontmatter["last_updated_at"] = ts
    frontmatter["distillation_state"] = "pending"
    pending = list(frontmatter.get("pending_reason", []))
    if "new-snippets" not in pending:
        pending.append("new-snippets")
    frontmatter["pending_reason"] = pending
    frontmatter["preview"] = preview_from_text(
        sections["summary"],
        f"Open thread with {snippet_id} captured; summary pending.",
    )

    updated = [relpath(path, root)]
    created_paths = updated.copy() if created else []
    if not dry_run:
        _write_thread(path, frontmatter, sections)
        updated.extend(rebuild_open_threads_view(root))
        updated.extend(rebuild_pending_distillation_view(root))
        updated.extend(rebuild_workspace_readme(root))

    return {
        "thread_path": relpath(path, root),
        "thread_id": frontmatter["id"],
        "thread_title": frontmatter["title"],
        "created": created,
        "snippet_id": snippet_id,
        "distillation_state": frontmatter["distillation_state"],
        "paths_created": created_paths,
        "paths_updated": updated,
    }


def get_thread_status(
    *,
    thread_path: str | None = None,
    thread_slug: str | None = None,
    workspace_root: str | None = None,
) -> dict[str, object]:
    root = resolve_workspace_root(workspace_root)
    if thread_path:
        path = Path(thread_path).resolve()
    elif thread_slug:
        path = thread_path_from_slug(root, thread_slug)
    else:
        raise WorkspaceError(
            "missing_thread_target",
            "One of --thread-path or --thread-slug is required.",
            "Pass a thread path or slug.",
        )

    frontmatter, sections = _load_thread(path)
    snippets = [line for line in sections["snippets"].splitlines() if line.startswith("### snp-")]
    return {
        "thread_path": relpath(path, root),
        "thread_id": frontmatter["id"],
        "title": frontmatter["title"],
        "preview": frontmatter["preview"],
        "thread_status": frontmatter["thread_status"],
        "distillation_state": frontmatter["distillation_state"],
        "last_updated_at": frontmatter["last_updated_at"],
        "open_questions": sections["open_questions"],
        "candidate_action_items": sections["candidate_action_items"],
        "primary_topic_refs": frontmatter.get("primary_topic_refs", []),
        "primary_entity_refs": frontmatter.get("primary_entity_refs", []),
        "action_item_refs": frontmatter.get("action_item_refs", []),
        "snippet_count": len(snippets),
    }


def sync_thread_state(
    *,
    thread_path: str,
    workspace_root: str | None = None,
    canonical_action_items: list[dict[str, Any]] | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    """Refresh thread metadata and related views after direct agent edits."""
    root = resolve_workspace_root(workspace_root)
    path = Path(thread_path).resolve()
    frontmatter, sections = _load_thread(path)

    now = current_timestamp()
    frontmatter["preview"] = preview_from_text(sections["summary"], "Open thread with captured notes.")
    frontmatter["last_updated_at"] = now
    frontmatter["light_distilled_at"] = now
    frontmatter["distillation_state"] = "pending"

    pending = list(frontmatter.get("pending_reason", []))
    if "new-snippets" not in pending:
        pending.append("new-snippets")
    frontmatter["pending_reason"] = pending

    action_item_paths_updated: list[str] = []
    if canonical_action_items:
        action_item_result = upsert_action_items(
            workspace_root=str(root),
            items=canonical_action_items,
            source_thread_ref=frontmatter["id"],
            dry_run=dry_run,
        )
        frontmatter["action_item_refs"] = list(action_item_result["action_item_refs"])
        action_item_paths_updated.extend(action_item_result["paths_updated"])

    updated = [relpath(path, root)]
    if not dry_run:
        _write_thread(path, frontmatter, sections)
        if canonical_action_items:
            updated.extend(rebuild_static_views(root))
        updated.extend(rebuild_open_threads_view(root))
        updated.extend(rebuild_pending_distillation_view(root))
        updated.extend(rebuild_workspace_readme(root))
        updated.extend(action_item_paths_updated)

    return {
        "thread_path": relpath(path, root),
        "thread_id": frontmatter["id"],
        "light_distilled_at": frontmatter["light_distilled_at"],
        "paths_updated": updated,
        "action_item_refs": frontmatter.get("action_item_refs", []),
    }
