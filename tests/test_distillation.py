from __future__ import annotations

from pathlib import Path

from notes_workspace.bootstrap import bootstrap_workspace
from notes_workspace.distillation import apply_distillation_result, resume_pending
from notes_workspace.frontmatter import load_markdown, write_markdown
from notes_workspace.imports import ingest_document, sync_import_state
from notes_workspace.threads import capture_note
from notes_workspace.topics import upsert_topics


def _create_thread(tmp_path: Path, *, slug: str, title: str, body: str, timestamp: str) -> Path:
    bootstrap_workspace(workspace_root=str(tmp_path))
    capture = capture_note(
        thread_slug=slug,
        thread_title=title,
        stdin_body=body,
        timestamp=timestamp,
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )
    return tmp_path / capture["thread_path"]


def _replace_summary(thread_path: Path, summary: str) -> None:
    frontmatter, body = load_markdown(thread_path)
    body = body.replace("Summary pending. [sources: ]", summary)
    write_markdown(thread_path, frontmatter, body)


def test_apply_distillation_result_creates_topic_and_marks_thread_complete(tmp_path: Path) -> None:
    """Intent: deep-distillation apply should create canonical topics and mark the source thread complete without forcing closure."""
    thread_path = _create_thread(
        tmp_path,
        slug="robot-debugging",
        title="Robot Debugging",
        body="Billy investigated Rover 3 connectivity dropouts.",
        timestamp="2026-03-27T09:00:00Z",
    )
    _replace_summary(
        thread_path,
        "Billy investigated Rover 3 connectivity dropouts and isolated the issue to the CAN bus. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
    )

    result = apply_distillation_result(
        thread_path=str(thread_path),
        workspace_root=str(tmp_path),
        rebuild_views=True,
        update={
            "source_patch": {
                "distillation_state": "complete",
                "pending_reason": [],
                "primary_entity_refs": ["top-systems-rover-3"],
            },
            "topic_upserts": [
                {
                    "type": "systems",
                    "title": "Rover 3",
                    "summary_markdown": "Rover 3 is experiencing intermittent connectivity dropouts on the CAN bus. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                    "current_understanding_markdown": "Current evidence points to CAN bus instability rather than power loss.",
                    "key_facts_markdown": "- Connectivity dropouts are reproducible.\n- The issue appears on the CAN bus.",
                    "related_topics_markdown": "- `Billy` is the current investigator.",
                    "recent_evidence_markdown": "- Robot Debugging thread observed the dropout pattern. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                    "change_history_markdown": "- 2026-03-27: Created from the Robot Debugging thread after isolating CAN bus involvement. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                    "entity": True,
                }
            ],
            "action_item_upserts": [
                {
                    "kind": "task",
                    "title": "Retest Rover 3 CAN bus connectivity",
                    "summary_markdown": "Retest Rover 3 CAN bus connectivity. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                    "current_state_markdown": "Open and awaiting execution.",
                    "evidence_markdown": "Derived from the Robot Debugging thread. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                    "linked_topic_refs": ["top-systems-rover-3"],
                    "confidence": "explicit",
                }
            ],
        },
    )

    topic_path = tmp_path / "memory" / "topics" / "systems" / "rover-3.md"
    assert topic_path.exists()
    topic_frontmatter, topic_body = load_markdown(topic_path)
    assert topic_frontmatter["doc_type"] == "topic"
    assert topic_frontmatter["id"] == "top-systems-rover-3"
    assert "CAN bus instability" in topic_body

    thread_frontmatter, _ = load_markdown(thread_path)
    assert thread_frontmatter["distillation_state"] == "complete"
    assert thread_frontmatter["deep_distilled_at"]
    assert thread_frontmatter["thread_status"] == "open"
    assert "top-systems-rover-3" in thread_frontmatter["primary_topic_refs"]
    assert result["topic_refs"] == ["top-systems-rover-3"]

    systems_index = (tmp_path / "memory" / "topics" / "systems" / "index.md").read_text(encoding="utf-8")
    assert "Rover 3" in systems_index


def test_apply_distillation_result_updates_existing_topic_and_can_close_thread(tmp_path: Path) -> None:
    """Intent: deep-distillation apply should update an existing topic and move a completed thread into closed storage when requested."""
    bootstrap_workspace(workspace_root=str(tmp_path))
    upsert_topics(
        workspace_root=str(tmp_path),
        items=[
            {
                "type": "systems",
                "title": "Rover 3",
                "summary_markdown": "Rover 3 has intermittent connectivity issues.",
                "current_understanding_markdown": "The exact root cause is still unclear.",
                "key_facts_markdown": "- Issue is intermittent.",
                "related_topics_markdown": "No related topics yet.",
                "recent_evidence_markdown": "- Prior observations were inconclusive.",
                "change_history_markdown": "- 2026-03-26: Initial topic created.",
                "entity": True,
            }
        ],
    )
    capture = capture_note(
        thread_slug="robot-debugging",
        thread_title="Robot Debugging",
        stdin_body="Billy confirmed the issue is on the CAN bus.",
        timestamp="2026-03-27T09:00:00Z",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )
    thread_path = tmp_path / capture["thread_path"]

    result = apply_distillation_result(
        thread_path=str(thread_path),
        workspace_root=str(tmp_path),
        rebuild_views=True,
        close_thread=True,
        update={
            "source_patch": {
                "distillation_state": "complete",
                "pending_reason": [],
            },
            "topic_upserts": [
                {
                    "id": "top-systems-rover-3",
                    "type": "systems",
                    "title": "Rover 3",
                    "summary_markdown": "Rover 3 connectivity issues are now understood as CAN bus dropouts. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                    "current_understanding_markdown": "The current best understanding is that CAN bus instability is the active cause.",
                    "key_facts_markdown": "- Billy confirmed CAN bus involvement.",
                    "related_topics_markdown": "- Related work is tracked in the Robot Debugging thread.",
                    "recent_evidence_markdown": "- Robot Debugging confirmed the CAN bus issue. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                    "change_history_markdown": "- 2026-03-27: Updated current understanding from unclear to CAN bus instability. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                    "entity": True,
                }
            ],
            "action_item_upserts": [],
        },
    )

    closed_thread_path = tmp_path / result["source_path"]
    assert closed_thread_path.exists()
    assert "/closed/" in str(closed_thread_path)
    assert not thread_path.exists()

    updated_topic = (tmp_path / "memory" / "topics" / "systems" / "rover-3.md").read_text(encoding="utf-8")
    assert "CAN bus instability" in updated_topic

    open_threads_view = (tmp_path / "memory" / "views" / "open-threads.md").read_text(encoding="utf-8")
    assert "Robot Debugging" not in open_threads_view


def test_apply_distillation_result_can_leave_thread_pending_for_user_resolution(tmp_path: Path) -> None:
    """Intent: blocked deep distillation should keep the source pending and preserve a recovery path."""
    thread_path = _create_thread(
        tmp_path,
        slug="power-decision",
        title="Power Decision",
        body="The team is split between 12V and 24V.",
        timestamp="2026-03-27T09:00:00Z",
    )

    apply_distillation_result(
        thread_path=str(thread_path),
        workspace_root=str(tmp_path),
        rebuild_views=True,
        update={
            "source_patch": {
                "distillation_state": "pending",
                "pending_reason": ["awaiting-user-resolution"],
            },
            "topic_upserts": [],
            "action_item_upserts": [],
        },
    )

    frontmatter, _ = load_markdown(thread_path)
    assert frontmatter["distillation_state"] == "pending"
    assert "awaiting-user-resolution" in frontmatter["pending_reason"]

    pending = resume_pending(workspace_root=str(tmp_path))
    assert pending["total"] == 1
    assert pending["items"][0]["title"] == "Power Decision"


def test_apply_distillation_result_can_complete_import_record_and_create_topic(tmp_path: Path) -> None:
    """Intent: deep-distillation apply should work on import records as well as threads."""
    bootstrap_workspace(workspace_root=str(tmp_path))
    source = tmp_path / "requirements.txt"
    source.write_text("Rover 3 must complete a CAN bus retest before release.\n", encoding="utf-8")
    ingest = ingest_document(
        source_path=str(source),
        title="Robot Requirements",
        imported_at="2026-03-27T09:00:00Z",
        workspace_root=str(tmp_path),
    )
    import_record = tmp_path / ingest["import_record_path"]
    frontmatter, body = load_markdown(import_record)
    body = body.replace(
        "Source summary pending.",
        "This document states that Rover 3 must complete a CAN bus retest before release. [sources: imp-2026-03-27-robot-requirements#txt-0001]",
    )
    write_markdown(import_record, frontmatter, body)
    sync_import_state(import_record_path=str(import_record), workspace_root=str(tmp_path))

    result = apply_distillation_result(
        import_record_path=str(import_record),
        workspace_root=str(tmp_path),
        rebuild_views=True,
        update={
            "source_patch": {
                "distillation_state": "complete",
                "pending_reason": [],
                "primary_topic_refs": ["top-systems-rover-3"],
                "primary_entity_refs": ["top-systems-rover-3"],
            },
            "topic_upserts": [
                {
                    "type": "systems",
                    "title": "Rover 3",
                    "summary_markdown": "Rover 3 requires a CAN bus retest before release. [sources: imp-2026-03-27-robot-requirements#txt-0001]",
                    "current_understanding_markdown": "Release remains gated on CAN bus retest completion.",
                    "key_facts_markdown": "- CAN bus retest is a release gate.",
                    "related_topics_markdown": "No related topics yet.",
                    "recent_evidence_markdown": "- Robot Requirements defines the release gate. [sources: imp-2026-03-27-robot-requirements#txt-0001]",
                    "change_history_markdown": "- 2026-03-27: Topic created from imported requirements. [sources: imp-2026-03-27-robot-requirements#txt-0001]",
                    "entity": True,
                }
            ],
            "action_item_upserts": [],
        },
    )

    import_frontmatter, _ = load_markdown(import_record)
    assert import_frontmatter["distillation_state"] == "complete"
    assert import_frontmatter["deep_distilled_at"]
    assert "top-systems-rover-3" in import_frontmatter["primary_topic_refs"]
    assert result["topic_refs"] == ["top-systems-rover-3"]

    topic_path = tmp_path / "memory" / "topics" / "systems" / "rover-3.md"
    assert topic_path.exists()
