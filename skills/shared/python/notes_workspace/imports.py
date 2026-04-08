"""Document ingestion and import-record sync operations."""

from __future__ import annotations

import re
import shutil
import subprocess
import zipfile
import os
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from .documents import (
    parse_import_record_body,
    preview_from_text,
    render_import_record_body,
    render_import_text_body,
)
from .errors import WorkspaceError
from .frontmatter import load_markdown, write_markdown
from .locks import acquire_lock
from .paths import imports_root, relpath, resolve_workspace_root
from .time_utils import current_timestamp
from .views import rebuild_pending_distillation_view, rebuild_static_views, rebuild_workspace_readme


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "import"


def _year(timestamp: str) -> str:
    return timestamp[:4]


def _import_paths(root: Path, *, imported_at: str, slug: str, ext: str) -> dict[str, Path]:
    year = _year(imported_at)
    date_prefix = imported_at[:10]
    normalized_ext = ext.lower().lstrip(".")
    source_name = f"{date_prefix}-{slug}.{normalized_ext}"
    base_name = f"{date_prefix}-{slug}.md"
    return {
        "source": imports_root(root) / "files" / year / source_name,
        "text": imports_root(root) / "text" / year / base_name,
        "record": imports_root(root) / "records" / year / base_name,
    }


def _read_text_input(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_docx_input(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            xml_bytes = archive.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise WorkspaceError(
            "invalid_docx_input",
            f"Could not read DOCX document {path.name!r}.",
            "Provide a valid .docx file.",
        ) from exc
    root = ElementTree.fromstring(xml_bytes)
    paragraphs: list[str] = []
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    for paragraph in root.findall(".//w:p", namespace):
        runs = paragraph.findall(".//w:t", namespace)
        text = "".join(run.text or "" for run in runs).strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def _read_pdf_input(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["pdftotext", str(path), "-"],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise WorkspaceError(
            "missing_pdf_text_extractor",
            "PDF ingestion requires a local text extractor such as `pdftotext`.",
            "Install `pdftotext` or ingest a text/markdown/docx source instead.",
        ) from exc
    if completed.returncode != 0:
        raise WorkspaceError(
            "pdf_text_extraction_failed",
            completed.stderr.strip() or f"Could not extract text from {path.name!r}.",
            "Confirm the PDF is readable and retry.",
        )
    return completed.stdout


def _normalized_source_text(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower().lstrip(".")
    if ext in {"md", "txt"}:
        return ext, _read_text_input(path)
    if ext == "docx":
        return ext, _read_docx_input(path)
    if ext == "pdf":
        return ext, _read_pdf_input(path)
    raise WorkspaceError(
        "unsupported_import_format",
        f"Unsupported import format {path.suffix or '<none>'!r}.",
        "Use .md, .txt, .docx, or .pdf.",
    )


def _chunk_text(text: str) -> list[tuple[str, str]]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if "\f" in text:
        pages = [page.strip() for page in text.split("\f") if page.strip()]
        return [(f"page {index}", page) for index, page in enumerate(pages, start=1)]

    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    if not blocks:
        return [("section 1", "(No extracted text.)")]

    chunks: list[tuple[str, str]] = []
    current: list[str] = []
    current_len = 0
    for block in blocks:
        block_len = len(block)
        if current and current_len + block_len + 2 > 1500:
            chunks.append((f"section {len(chunks) + 1}", "\n\n".join(current)))
            current = [block]
            current_len = block_len
        else:
            current.append(block)
            current_len += block_len + (2 if current_len else 0)
    if current:
        chunks.append((f"section {len(chunks) + 1}", "\n\n".join(current)))
    return chunks


def _new_import_frontmatter(
    *,
    title: str,
    slug: str,
    source_filename: str,
    source_path: str,
    normalized_text_path: str,
    source_format: str,
    imported_at: str,
) -> dict[str, Any]:
    return {
        "doc_type": "import-record",
        "id": f"imp-{imported_at[:10]}-{slug}",
        "title": title,
        "slug": slug,
        "preview": "Imported source with summary pending.",
        "source_filename": source_filename,
        "source_path": source_path,
        "normalized_text_path": normalized_text_path,
        "source_format": source_format,
        "imported_at": imported_at,
        "updated_at": imported_at,
        "distillation_state": "pending",
        "light_distilled_at": None,
        "deep_distilled_at": None,
        "last_deep_distill_attempt_at": None,
        "pending_reason": ["new-import"],
        "primary_topic_refs": [],
        "primary_entity_refs": [],
        "action_item_refs": [],
    }


def ingest_document(
    *,
    source_path: str,
    title: str,
    slug: str | None = None,
    imported_at: str | None = None,
    workspace_root: str | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    root = resolve_workspace_root(workspace_root)
    source = Path(source_path).resolve()
    if not source.exists():
        raise WorkspaceError(
            "source_file_not_found",
            f"Source file {source} does not exist.",
            "Pass an existing file path.",
        )

    imported_ts = imported_at or current_timestamp()
    normalized_slug = slug or _slugify(title)
    source_format, normalized_text = _normalized_source_text(source)
    paths = _import_paths(root, imported_at=imported_ts, slug=normalized_slug, ext=source_format)
    source_rel = os.path.relpath(paths["source"], paths["record"].parent)
    text_rel = os.path.relpath(paths["text"], paths["record"].parent)

    text_frontmatter = {
        "doc_type": "import-text",
        "id": f"imt-{imported_ts[:10]}-{normalized_slug}",
        "title": title,
        "slug": normalized_slug,
        "derived_from_import": f"imp-{imported_ts[:10]}-{normalized_slug}",
        "source_format": source_format,
        "generated_at": imported_ts,
    }
    text_body = render_import_text_body(title=title, chunks=_chunk_text(normalized_text))

    record_frontmatter = _new_import_frontmatter(
        title=title,
        slug=normalized_slug,
        source_filename=source.name,
        source_path=source_rel,
        normalized_text_path=text_rel,
        source_format=source_format,
        imported_at=imported_ts,
    )
    record_body = render_import_record_body(
        title=title,
        source_summary="Source summary pending.",
        open_questions="No open questions yet.",
        candidate_action_items="No candidate action items yet.",
        distillation_notes="Awaiting lightweight distillation.",
    )

    paths_created = [relpath(paths["source"], root), relpath(paths["text"], root), relpath(paths["record"], root)]
    paths_updated = list(paths_created)
    with acquire_lock(workspace_root=str(root), name=f"import-{paths['record'].stem}"):
        if not dry_run:
            paths["source"].parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, paths["source"])
            write_markdown(paths["text"], text_frontmatter, text_body)
            write_markdown(paths["record"], record_frontmatter, record_body)
            with acquire_lock(workspace_root=str(root), name="views"):
                paths_updated.extend(rebuild_static_views(root))
                paths_updated.extend(rebuild_pending_distillation_view(root))
                paths_updated.extend(rebuild_workspace_readme(root))

    return {
        "import_record_path": relpath(paths["record"], root),
        "import_id": record_frontmatter["id"],
        "normalized_text_path": relpath(paths["text"], root),
        "source_copy_path": relpath(paths["source"], root),
        "distillation_state": record_frontmatter["distillation_state"],
        "paths_created": paths_created,
        "paths_updated": paths_updated,
    }


def sync_import_state(
    *,
    import_record_path: str,
    workspace_root: str | None = None,
    canonical_action_items: list[dict[str, Any]] | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    from .action_items import upsert_action_items

    root = resolve_workspace_root(workspace_root)
    path = Path(import_record_path).resolve()
    with acquire_lock(workspace_root=str(root), name=f"import-{path.stem}"):
        frontmatter, body = load_markdown(path)
        parsed = parse_import_record_body(body)
        now = current_timestamp()

        frontmatter["preview"] = preview_from_text(parsed["source_summary"], "Imported source with captured text.")
        frontmatter["updated_at"] = now
        frontmatter["light_distilled_at"] = now
        frontmatter["distillation_state"] = "pending"
        pending = list(frontmatter.get("pending_reason", []))
        if "new-import" not in pending:
            pending.append("new-import")
        frontmatter["pending_reason"] = pending

        action_item_paths_updated: list[str] = []
        if canonical_action_items:
            with acquire_lock(workspace_root=str(root), name="action-items"):
                action_item_result = upsert_action_items(
                    workspace_root=str(root),
                    items=canonical_action_items,
                    source_import_ref=frontmatter["id"],
                    dry_run=dry_run,
                )
            frontmatter["action_item_refs"] = list(action_item_result["action_item_refs"])
            action_item_paths_updated.extend(action_item_result["paths_updated"])

        updated = [relpath(path, root)]
        if not dry_run:
            write_markdown(path, frontmatter, body)
            with acquire_lock(workspace_root=str(root), name="views"):
                if canonical_action_items:
                    updated.extend(rebuild_static_views(root))
                updated.extend(rebuild_pending_distillation_view(root))
                updated.extend(rebuild_workspace_readme(root))
            updated.extend(action_item_paths_updated)

    return {
        "import_record_path": relpath(path, root),
        "import_id": frontmatter["id"],
        "light_distilled_at": frontmatter["light_distilled_at"],
        "paths_updated": updated,
        "action_item_refs": frontmatter.get("action_item_refs", []),
    }
