"""Generated view rebuilding."""

from __future__ import annotations

from pathlib import Path

from .documents import parse_thread_body, preview_from_text, render_generated_doc
from .frontmatter import load_markdown, write_markdown
from .action_items import list_action_items
from .topics import custom_type_dir_name, list_topics
from .paths import (
    TOPIC_TYPES,
    action_items_root,
    imports_root,
    memory_root,
    relpath,
    resolve_workspace_root,
    topics_root,
    view_root,
)
from .time_utils import current_timestamp


def _list_open_threads(workspace_root: Path) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    today = current_timestamp()[:10]
    for path in sorted((memory_root(workspace_root) / "threads" / "open").glob("*/*.md")):
        frontmatter, body = load_markdown(path)
        parsed = parse_thread_body(body)
        open_questions_lines = [
            line.strip("- ").strip()
            for line in parsed["open_questions"].splitlines()
            if line.strip() and not line.lower().startswith("no ")
        ]
        results.append(
            {
                "path": path,
                "title": frontmatter["title"],
                "preview": frontmatter.get("preview", ""),
                "last_captured_at": frontmatter.get("last_captured_at", frontmatter["opened_at"]),
                "last_updated_at": frontmatter["last_updated_at"],
                "distillation_state": frontmatter["distillation_state"],
                "stale": frontmatter.get("last_captured_at", frontmatter["opened_at"])[:10] != today,
                "open_question_count": len(open_questions_lines),
            }
        )
    results.sort(key=lambda item: (item["last_captured_at"], item["last_updated_at"]), reverse=True)
    return results


def rebuild_open_threads_view(workspace_root: Path) -> list[str]:
    workspace_root = resolve_workspace_root(str(workspace_root))
    threads = _list_open_threads(workspace_root)
    active_lines: list[str] = []
    stale_lines: list[str] = []
    for item in threads:
        rel = relpath(item["path"], workspace_root)
        line = (
            f"- `{item['title']}` "
            f"({rel}) | captured `{item['last_captured_at']}` | updated `{item['last_updated_at']}` | distillation `{item['distillation_state']}`\n"
            f"  Preview: {item['preview'] or 'No preview yet.'}\n"
            f"  Open question count: {item['open_question_count']}"
        )
        if item["stale"]:
            stale_lines.append(line)
        else:
            active_lines.append(line)

    body = render_generated_doc(
        title="Open Threads",
        sections=[
            (
                "## Active Threads",
                "\n".join(active_lines) if active_lines else "No active open threads.",
            ),
            (
                "## Stale-Open Threads",
                "\n".join(stale_lines) if stale_lines else "No stale-open threads.",
            ),
        ],
    )
    path = view_root(workspace_root) / "open-threads.md"
    fm = {
        "doc_type": "generated-view",
        "view_type": "open-threads",
        "preview": preview_from_text(
            f"{len(threads)} open threads tracked.",
            "Lists open threads and stale-open threads.",
        ),
        "updated_at": current_timestamp(),
        "generated": True,
    }
    write_markdown(path, fm, body)
    return [relpath(path, workspace_root)]


def rebuild_pending_distillation_view(workspace_root: Path) -> list[str]:
    workspace_root = resolve_workspace_root(str(workspace_root))
    pending_lines: list[str] = []
    for path in sorted((memory_root(workspace_root) / "threads").glob("*/*/*.md")):
        frontmatter, _ = load_markdown(path)
        if frontmatter.get("distillation_state") != "pending":
            continue
        reasons = ", ".join(frontmatter.get("pending_reason", [])) or "pending"
        thread_state = frontmatter.get("thread_status", "unknown")
        pending_lines.append(
            f"- `thread` `{frontmatter['title']}` ({relpath(path, workspace_root)}) | state `{thread_state}` | reasons `{reasons}` | last attempted `{frontmatter.get('last_deep_distill_attempt_at')}`"
        )
    for path in sorted((imports_root(workspace_root) / "records").glob("*/*.md")):
        frontmatter, _ = load_markdown(path)
        if frontmatter.get("distillation_state") != "pending":
            continue
        reasons = ", ".join(frontmatter.get("pending_reason", [])) or "pending"
        pending_lines.append(
            f"- `import` `{frontmatter['title']}` ({relpath(path, workspace_root)}) | state `pending` | reasons `{reasons}` | last attempted `{frontmatter.get('last_deep_distill_attempt_at')}`"
        )
    body = render_generated_doc(
        title="Pending Distillation",
        sections=[
            (
                "## Pending Items",
                "\n".join(pending_lines) if pending_lines else "No pending distillation items.",
            )
        ],
    )
    path = view_root(workspace_root) / "pending-distillation.md"
    fm = {
        "doc_type": "generated-view",
        "view_type": "pending-distillation",
        "preview": preview_from_text(
            f"{len(pending_lines)} items currently need deep reconciliation.",
            "Lists anything that still needs deep reconciliation.",
        ),
        "updated_at": current_timestamp(),
        "generated": True,
    }
    write_markdown(path, fm, body)
    return [relpath(path, workspace_root)]


def rebuild_static_views(workspace_root: Path) -> list[str]:
    workspace_root = resolve_workspace_root(str(workspace_root))
    updated: list[str] = []
    topics = list_topics(workspace_root=str(workspace_root))

    action_item_result = list_action_items(workspace_root=str(workspace_root), include_closed=False)
    task_lines: list[str] = []
    question_lines: list[str] = []
    import_lines: list[str] = []
    for item in action_item_result["items"]:
        line = (
            f"- `{item['title']}` ({item['path']}) | status `{item['status']}` | "
            f"confidence `{item['confidence']}`"
        )
        if item["owner_topic_refs"]:
            line += f" | owners `{', '.join(item['owner_topic_refs'])}`"
        if item["linked_topic_refs"]:
            line += f" | topics `{', '.join(item['linked_topic_refs'])}`"
        if item["due_at"]:
            line += f" | due `{item['due_at']}`"
        if item["kind"] == "task":
            task_lines.append(line)
        else:
            question_lines.append(line)

    for path in sorted((imports_root(workspace_root) / "records").glob("*/*.md")):
        frontmatter, _ = load_markdown(path)
        import_lines.append(
            f"- `{frontmatter['title']}` ({relpath(path, workspace_root)}) | format `{frontmatter['source_format']}` | "
            f"imported `{frontmatter['imported_at']}` | distillation `{frontmatter['distillation_state']}`"
        )

    topic_type_lines: list[str] = []
    typed_topics: dict[str, list[dict[str, object]]] = {topic_type: [] for topic_type in TOPIC_TYPES}
    custom_groups: dict[str, list[dict[str, object]]] = {}
    for item in topics:
        if item["type"] == "custom":
            custom_name = str(item["custom_type"] or "uncategorized")
            custom_groups.setdefault(custom_name, []).append(item)
        else:
            typed_topics[str(item["type"])].append(item)

    for topic_type in TOPIC_TYPES:
        if topic_type == "custom":
            count = sum(len(items) for items in custom_groups.values())
            topic_type_lines.append(f"- `custom` ({count})")
        else:
            topic_type_lines.append(f"- `{topic_type}` ({len(typed_topics[topic_type])})")

    static_views = {
        view_root(workspace_root) / "imports.md": (
            "Imports",
            "imports",
            "Lists imported source records and their distillation state.",
            [("## Imports", "\n".join(import_lines) if import_lines else "No imported sources yet.")],
        ),
        view_root(workspace_root) / "action-items.md": (
            "Action Items",
            "action-items",
            "Lists open tasks and open questions.",
            [
                ("## Open Tasks", "\n".join(task_lines) if task_lines else "No open tasks yet."),
                ("## Open Questions", "\n".join(question_lines) if question_lines else "No open questions yet."),
            ],
        ),
        topics_root(workspace_root) / "index.md": (
            "Topics Index",
            "topics-index",
            "Links to typed topic indexes and recently updated topics.",
            [("## Topic Types", "\n".join(topic_type_lines))],
        ),
    }

    for path, (title, view_type, preview, sections) in static_views.items():
        fm = {
            "doc_type": "generated-view",
            "view_type": view_type,
            "preview": preview[:240],
            "updated_at": current_timestamp(),
            "generated": True,
        }
        write_markdown(path, fm, render_generated_doc(title=title, sections=sections))
        updated.append(relpath(path, workspace_root))

    for topic_type in TOPIC_TYPES:
        if topic_type == "custom":
            continue
        path = topics_root(workspace_root) / topic_type / "index.md"
        lines = []
        for item in typed_topics[topic_type]:
            lines.append(
                f"- `{item['title']}` ({item['path']}) | freshness `{item['freshness']}` | updated `{item['updated_at']}`\n"
                f"  Preview: {item['preview']}"
            )
        fm = {
            "doc_type": "generated-view",
            "view_type": f"topic-index-{topic_type}",
            "preview": f"Lists topic files in `{topic_type}`."[:240],
            "updated_at": current_timestamp(),
            "generated": True,
        }
        write_markdown(
            path,
            fm,
            render_generated_doc(
                title=f"{topic_type.title()} Index",
                sections=[("## Topics", "\n".join(lines) if lines else f"No topics in `{topic_type}` yet.")],
            ),
        )
        updated.append(relpath(path, workspace_root))

    custom_index = topics_root(workspace_root) / "custom" / "index.md"
    custom_lines = []
    for custom_type, items in sorted(custom_groups.items()):
        custom_lines.append(f"- `{custom_type}` ({len(items)})")
    write_markdown(
        custom_index,
        {
            "doc_type": "generated-view",
            "view_type": "topic-index-custom",
            "preview": "Lists approved custom topic-type groups.",
            "updated_at": current_timestamp(),
            "generated": True,
        },
        render_generated_doc(
            title="Custom Topic Types",
            sections=[("## Custom Types", "\n".join(custom_lines) if custom_lines else "No custom topic types yet.")],
        ),
    )
    updated.append(relpath(custom_index, workspace_root))

    for custom_type, items in sorted(custom_groups.items()):
        custom_dir = topics_root(workspace_root) / "custom" / custom_type_dir_name(custom_type)
        custom_type_lines = []
        for item in items:
            custom_type_lines.append(
                f"- `{item['title']}` ({item['path']}) | freshness `{item['freshness']}` | updated `{item['updated_at']}`\n"
                f"  Preview: {item['preview']}"
            )
        write_markdown(
            custom_dir / "index.md",
            {
                "doc_type": "generated-view",
                "view_type": f"topic-index-custom-{custom_type_dir_name(custom_type)}",
                "preview": f"Lists topic files in custom type `{custom_type}`."[:240],
                "updated_at": current_timestamp(),
                "generated": True,
            },
            render_generated_doc(
                title=f"{custom_type.title()} Index",
                sections=[("## Topics", "\n".join(custom_type_lines) if custom_type_lines else "No topics yet.")],
            ),
        )
        updated.append(relpath(custom_dir / "index.md", workspace_root))

    return updated


def rebuild_workspace_readme(workspace_root: Path) -> list[str]:
    workspace_root = resolve_workspace_root(str(workspace_root))
    open_threads = len(list((memory_root(workspace_root) / "threads" / "open").glob("*/*.md")))
    imports_count = len(list((imports_root(workspace_root) / "records").glob("*/*.md")))
    open_action_items = len(list((action_items_root(workspace_root) / "open").glob("*/*.md")))
    body = render_generated_doc(
        title="Workspace Memory Index",
        sections=[
            ("## Workspace Summary", f"Open threads: {open_threads}\nImports: {imports_count}\nAction items: {open_action_items}"),
            (
                "## Key Navigation",
                "\n".join(
                    [
                        "- `memory/views/open-threads.md`",
                        "- `memory/views/pending-distillation.md`",
                        "- `memory/views/action-items.md`",
                        "- `memory/views/imports.md`",
                        "- `memory/topics/index.md`",
                    ]
                ),
            ),
            ("## Pending Recovery", "See `memory/views/pending-distillation.md`."),
            ("## Active Work", "See `memory/views/open-threads.md` and `memory/views/action-items.md`."),
        ],
    )
    path = memory_root(workspace_root) / "README.md"
    write_markdown(
        path,
        {
            "doc_type": "workspace-entrypoint",
            "title": "Workspace Memory Index",
            "preview": "Workspace entrypoint linking to navigation, pending recovery, and active work views.",
            "updated_at": current_timestamp(),
            "generated": True,
        },
        body,
    )
    return [relpath(path, workspace_root)]


def rebuild_all_views(workspace_root: Path) -> list[str]:
    updated: list[str] = []
    updated.extend(rebuild_static_views(workspace_root))
    updated.extend(rebuild_open_threads_view(workspace_root))
    updated.extend(rebuild_pending_distillation_view(workspace_root))
    updated.extend(rebuild_workspace_readme(workspace_root))
    return updated
