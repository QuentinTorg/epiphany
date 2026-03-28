"""Coarse retrieval helpers for agent-led workspace queries."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .action_items import list_action_items
from .documents import parse_thread_body
from .frontmatter import load_markdown
from .paths import memory_root, relpath, resolve_workspace_root, view_root

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "did",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "last",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "who",
    "with",
}


def _query_terms(query: str) -> list[str]:
    terms = re.findall(r"[a-z0-9]+", query.lower())
    filtered = [term for term in terms if len(term) > 1 and term not in STOPWORDS]
    return filtered or terms[:5]


def _contains_all_terms(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return all(term in lowered for term in terms)


def _contains_any_term(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _score_text(text: str, terms: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for term in terms if term in lowered)


def _best_excerpt(text: str, terms: list[str], *, fallback: str, limit: int = 240) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return fallback[:limit]
    lowered = compact.lower()
    best_index = min((lowered.find(term) for term in terms if term in lowered), default=-1)
    if best_index < 0:
        return compact[:limit]
    start = max(0, best_index - 60)
    end = min(len(compact), start + limit)
    excerpt = compact[start:end]
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(compact):
        excerpt = excerpt + "..."
    return excerpt


def _safe_load(path: Path) -> tuple[dict[str, Any], str] | None:
    try:
        return load_markdown(path)
    except Exception:
        return None


def _candidate_from_thread(
    path: Path,
    root: Path,
    terms: list[str],
    *,
    topic: str | None,
    entity: str | None,
    source_thread: str | None,
    date_from: str | None,
    date_to: str | None,
) -> dict[str, Any] | None:
    loaded = _safe_load(path)
    if loaded is None:
        return None
    frontmatter, body = loaded
    if source_thread and frontmatter.get("id") != source_thread:
        return None
    if topic and topic not in frontmatter.get("primary_topic_refs", []):
        return None
    if entity and entity not in (frontmatter.get("primary_entity_refs", []) + frontmatter.get("primary_topic_refs", [])):
        return None
    effective_date = frontmatter.get("opened_at") or frontmatter.get("last_updated_at", "")
    if date_from and effective_date < date_from:
        return None
    if date_to and effective_date > date_to:
        return None

    parsed = parse_thread_body(body)
    title = frontmatter.get("title", path.stem)
    preview = frontmatter.get("preview", "")
    searchable = "\n".join(
        [
            title,
            preview,
            parsed["summary"],
            parsed["open_questions"],
            parsed["candidate_action_items"],
        ]
    )
    if terms and not _contains_any_term(searchable, terms):
        return None
    score = (
        _score_text(title, terms) * 4
        + _score_text(preview, terms) * 3
        + _score_text(parsed["summary"], terms) * 2
        + _score_text(parsed["open_questions"], terms)
        + _score_text(parsed["candidate_action_items"], terms)
    )
    return {
        "path": relpath(path, root),
        "doc_type": "thread",
        "title": title,
        "preview": preview,
        "score": score,
        "updated_at": frontmatter.get("last_updated_at"),
        "effective_date": effective_date,
        "status": frontmatter.get("thread_status"),
        "distillation_state": frontmatter.get("distillation_state"),
        "matched_terms": [term for term in terms if term in searchable.lower()],
        "excerpt": _best_excerpt(
            "\n".join([parsed["summary"], parsed["open_questions"], parsed["candidate_action_items"]]),
            terms,
            fallback=preview or title,
        ),
    }


def _candidate_from_action_item(item: dict[str, Any], terms: list[str]) -> dict[str, Any] | None:
    owner_refs = " ".join(item["owner_topic_refs"])
    linked_refs = " ".join(item["linked_topic_refs"])
    searchable = "\n".join(
        [
            item["title"],
            item["preview"],
            item["summary"],
            item["current_state"],
            owner_refs,
            linked_refs,
        ]
    )
    if terms and not _contains_any_term(searchable, terms):
        return None
    score = (
        _score_text(item["title"], terms) * 4
        + _score_text(item["preview"], terms) * 3
        + _score_text(item["summary"], terms) * 2
        + _score_text(item["current_state"], terms)
        + _score_text(owner_refs, terms) * 2
        + _score_text(linked_refs, terms)
    )
    return {
        "path": item["path"],
        "doc_type": "action-item",
        "title": item["title"],
        "preview": item["preview"],
        "score": score,
        "updated_at": item.get("updated_at"),
        "status": item["status"],
        "kind": item["kind"],
        "matched_terms": [term for term in terms if term in searchable.lower()],
        "excerpt": _best_excerpt(
            "\n".join([item["summary"], item["current_state"]]),
            terms,
            fallback=item["preview"] or item["title"],
        ),
    }


def _candidate_from_generic_doc(
    path: Path,
    root: Path,
    terms: list[str],
    *,
    topic: str | None,
    entity: str | None,
    source_import: str | None,
    date_from: str | None,
    date_to: str | None,
) -> dict[str, Any] | None:
    loaded = _safe_load(path)
    if loaded is None:
        return None
    frontmatter, body = loaded
    doc_type = frontmatter.get("doc_type")
    if doc_type == "thread":
        return None
    if source_import and source_import not in {frontmatter.get("id"), frontmatter.get("slug")}:
        if source_import not in frontmatter.get("source_import_refs", []):
            return None
    if topic and topic not in frontmatter.get("primary_topic_refs", []) and topic not in frontmatter.get("linked_topic_refs", []):
        return None
    entity_refs = (
        frontmatter.get("primary_entity_refs", [])
        + frontmatter.get("linked_topic_refs", [])
        + frontmatter.get("owner_topic_refs", [])
    )
    if entity and entity not in entity_refs:
        return None
    updated_at = (
        frontmatter.get("updated_at")
        or frontmatter.get("last_updated_at")
        or frontmatter.get("imported_at")
        or ""
    )
    if date_from and updated_at and updated_at < date_from:
        return None
    if date_to and updated_at and updated_at > date_to:
        return None

    title = frontmatter.get("title", path.stem)
    preview = frontmatter.get("preview", "")
    searchable = "\n".join([title, preview, body])
    if terms and not _contains_any_term(searchable, terms):
        return None
    score = (
        _score_text(title, terms) * 4
        + _score_text(preview, terms) * 3
        + _score_text(body, terms)
    )
    return {
        "path": relpath(path, root),
        "doc_type": doc_type or "markdown",
        "title": title,
        "preview": preview,
        "score": score,
        "updated_at": updated_at or None,
        "matched_terms": [term for term in terms if term in searchable.lower()],
        "excerpt": _best_excerpt(body, terms, fallback=preview or title),
    }


def _pending_warnings(
    root: Path,
    terms: list[str],
    *,
    topic: str | None,
    entity: str | None,
    source_thread: str | None,
) -> list[str]:
    warnings: list[str] = []
    for path in sorted((memory_root(root) / "threads").glob("*/*/*.md")):
        loaded = _safe_load(path)
        if loaded is None:
            continue
        frontmatter, body = loaded
        if frontmatter.get("doc_type") != "thread":
            continue
        if frontmatter.get("distillation_state") != "pending":
            continue
        if source_thread and frontmatter.get("id") != source_thread:
            continue
        if topic and topic not in frontmatter.get("primary_topic_refs", []):
            continue
        if entity and entity not in (frontmatter.get("primary_entity_refs", []) + frontmatter.get("primary_topic_refs", [])):
            continue
        parsed = parse_thread_body(body)
        searchable = "\n".join(
            [
                frontmatter.get("title", path.stem),
                frontmatter.get("preview", ""),
                parsed["summary"],
                parsed["open_questions"],
                parsed["candidate_action_items"],
            ]
        )
        if terms and not _contains_any_term(searchable, terms):
            continue
        warnings.append(
            f"Pending distillation may affect this answer: `{frontmatter.get('title', path.stem)}` ({relpath(path, root)})"
        )
    return warnings


def _view_navigation_paths(root: Path, terms: list[str]) -> list[str]:
    candidates = [
        memory_root(root) / "README.md",
        view_root(root) / "open-threads.md",
        view_root(root) / "pending-distillation.md",
        view_root(root) / "action-items.md",
        view_root(root) / "imports.md",
        memory_root(root) / "topics" / "index.md",
    ]
    results: list[str] = []
    readme_exists = (memory_root(root) / "README.md").exists()
    if readme_exists:
        results.append("memory/README.md")
    for path in candidates:
        if not path.exists():
            continue
        if path == memory_root(root) / "README.md":
            continue
        loaded = _safe_load(path)
        if loaded is None:
            continue
        frontmatter, body = loaded
        haystack = "\n".join([frontmatter.get("title", path.stem), frontmatter.get("preview", ""), body])
        if not terms or _contains_any_term(haystack, terms):
            results.append(relpath(path, root))
    return results


def query_memory(
    *,
    query: str,
    workspace_root: str | None = None,
    mode: str = "concise",
    topic: str | None = None,
    entity: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    source_thread: str | None = None,
    source_import: str | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> dict[str, object]:
    root = resolve_workspace_root(workspace_root)
    terms = _query_terms(query)
    candidates: list[dict[str, Any]] = []

    action_items = list_action_items(
        workspace_root=str(root),
        kind="all",
        topic=topic,
        entity=entity,
        date_from=date_from,
        date_to=date_to,
        source_thread=source_thread,
        source_import=source_import,
        include_closed=(mode == "research"),
    )
    for item in action_items["items"]:
        candidate = _candidate_from_action_item(item, terms)
        if candidate:
            candidates.append(candidate)

    for path in sorted((memory_root(root) / "threads").glob("*/*/*.md")):
        candidate = _candidate_from_thread(
            path,
            root,
            terms,
            topic=topic,
            entity=entity,
            source_thread=source_thread,
            date_from=date_from,
            date_to=date_to,
        )
        if candidate:
            candidates.append(candidate)

    generic_roots = [
        memory_root(root) / "README.md",
        view_root(root),
        memory_root(root) / "topics",
        memory_root(root) / "imports" / "records",
    ]
    seen_paths = {candidate["path"] for candidate in candidates}
    for generic_root in generic_roots:
        paths = [generic_root] if generic_root.is_file() else sorted(generic_root.rglob("*.md"))
        for path in paths:
            relative = relpath(path, root)
            if relative in seen_paths:
                continue
            candidate = _candidate_from_generic_doc(
                path,
                root,
                terms,
                topic=topic,
                entity=entity,
                source_import=source_import,
                date_from=date_from,
                date_to=date_to,
            )
            if candidate:
                candidates.append(candidate)
                seen_paths.add(relative)

    candidates.sort(key=lambda item: (-item["score"], item.get("updated_at") or "", item["path"]))
    total = len(candidates)
    sliced = candidates[offset:]
    if limit is None:
        limit = 5 if mode == "concise" else 12
    sliced = sliced[:limit]

    warnings = _pending_warnings(
        root,
        terms,
        topic=topic,
        entity=entity,
        source_thread=source_thread,
    )
    return {
        "query": query,
        "mode": mode,
        "terms": terms,
        "recommended_start_paths": _view_navigation_paths(root, terms),
        "candidates": sliced,
        "total": total,
        "offset": offset,
        "limit": limit,
        "pending_warnings": warnings,
    }
