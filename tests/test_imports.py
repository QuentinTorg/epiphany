from __future__ import annotations

from pathlib import Path

from notes_workspace.bootstrap import bootstrap_workspace
from notes_workspace.frontmatter import load_markdown, write_markdown
from notes_workspace.imports import ingest_document, sync_import_state


def test_ingest_document_copies_source_and_creates_normalized_text_and_record(tmp_path: Path) -> None:
    """Intent: document ingestion should preserve the original file, generate normalized text, and create a pending import record."""
    bootstrap_workspace(workspace_root=str(tmp_path))
    source = tmp_path / "requirements.txt"
    source.write_text("System requirements\n\nCAN bus retest is required.\n", encoding="utf-8")

    result = ingest_document(
        source_path=str(source),
        title="Robot Requirements",
        imported_at="2026-03-27T09:00:00Z",
        workspace_root=str(tmp_path),
    )

    source_copy = tmp_path / result["source_copy_path"]
    normalized_text = tmp_path / result["normalized_text_path"]
    import_record = tmp_path / result["import_record_path"]

    assert source_copy.exists()
    assert normalized_text.exists()
    assert import_record.exists()

    text_frontmatter, text_body = load_markdown(normalized_text)
    assert text_frontmatter["doc_type"] == "import-text"
    assert "### txt-0001 | section 1" in text_body

    record_frontmatter, record_body = load_markdown(import_record)
    assert record_frontmatter["doc_type"] == "import-record"
    assert record_frontmatter["distillation_state"] == "pending"
    assert record_frontmatter["pending_reason"] == ["new-import"]
    assert "## Source Summary" in record_body

    imports_view = (tmp_path / "memory" / "views" / "imports.md").read_text(encoding="utf-8")
    pending_view = (tmp_path / "memory" / "views" / "pending-distillation.md").read_text(encoding="utf-8")
    assert "Robot Requirements" in imports_view
    assert "Robot Requirements" in pending_view


def test_sync_import_state_refreshes_preview_after_direct_import_edit(tmp_path: Path) -> None:
    """Intent: direct agent edits to import-record prose should become operationally visible after the structural sync step."""
    bootstrap_workspace(workspace_root=str(tmp_path))
    source = tmp_path / "requirements.txt"
    source.write_text("System requirements\n\nCAN bus retest is required.\n", encoding="utf-8")

    result = ingest_document(
        source_path=str(source),
        title="Robot Requirements",
        imported_at="2026-03-27T09:00:00Z",
        workspace_root=str(tmp_path),
    )
    import_record = tmp_path / result["import_record_path"]

    frontmatter, body = load_markdown(import_record)
    body = body.replace(
        "Source summary pending.",
        "This document describes robot requirements and points to the CAN bus retest requirement in section 1. [sources: imp-2026-03-27-robot-requirements#txt-0001]",
    )
    body = body.replace("No open questions yet.", "- Does the retest require vendor signoff?")
    body = body.replace("No candidate action items yet.", "- Confirm retest acceptance criteria.")
    write_markdown(import_record, frontmatter, body)

    sync_import_state(import_record_path=str(import_record), workspace_root=str(tmp_path))

    refreshed_frontmatter, _ = load_markdown(import_record)
    assert "robot requirements" in refreshed_frontmatter["preview"].lower()
    imports_view = (tmp_path / "memory" / "views" / "imports.md").read_text(encoding="utf-8")
    assert "Robot Requirements" in imports_view
