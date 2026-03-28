from __future__ import annotations

import json
from pathlib import Path

from notes_workspace.action_items import list_action_items
from notes_workspace.bootstrap import bootstrap_workspace
from notes_workspace.frontmatter import load_markdown, write_markdown
from notes_workspace.threads import capture_note, sync_thread_state


def _create_thread(tmp_path: Path) -> Path:
    bootstrap_workspace(workspace_root=str(tmp_path))
    capture = capture_note(
        thread_slug="robot-debugging",
        thread_title="Robot Debugging",
        stdin_body="Billy investigated the connectivity issue.",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )
    return tmp_path / capture["thread_path"]


def test_thread_update_can_create_canonical_task_and_question_records(tmp_path: Path) -> None:
    """Intent: explicit action items in a thread update should become canonical action-item files."""
    thread_path = _create_thread(tmp_path)
    frontmatter, body = load_markdown(thread_path)
    body = body.replace(
        "Summary pending. [sources: ]",
        "Billy investigated robot connectivity and needs a follow-up. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
    )
    body = body.replace("No open questions yet.", "- Did the retest fix the dropout issue?")
    body = body.replace("No candidate action items yet.", "- Retest robot connectivity tomorrow.")
    write_markdown(thread_path, frontmatter, body)

    sync_thread_state(
        thread_path=str(thread_path),
        workspace_root=str(tmp_path),
        canonical_action_items=[
            {
                "kind": "task",
                "title": "Retest robot connectivity tomorrow",
                "summary_markdown": "Retest robot connectivity tomorrow. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "current_state_markdown": "Open and awaiting execution.",
                "evidence_markdown": "Captured from the thread summary and snippet evidence. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "priority": "high",
                "confidence": "explicit",
                "owner_topic_refs": ["top-people-billy"],
                "linked_topic_refs": ["top-systems-rover-3"],
            },
            {
                "kind": "question",
                "title": "Did the retest fix the dropout issue?",
                "summary_markdown": "Need to confirm whether the retest fixed the dropout issue. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "current_state_markdown": "Open pending retest results.",
                "evidence_markdown": "Derived from the unresolved question in the thread. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "confidence": "explicit",
                "linked_topic_refs": ["top-systems-rover-3"],
            },
        ],
    )

    open_items = list((tmp_path / "memory" / "action-items" / "open").rglob("*.md"))
    assert len(open_items) == 2

    action_view = (tmp_path / "memory" / "views" / "action-items.md").read_text(encoding="utf-8")
    assert "Retest robot connectivity tomorrow" in action_view
    assert "Did the retest fix the dropout issue?" in action_view


def test_canonical_action_item_records_capture_required_metadata(tmp_path: Path) -> None:
    """Intent: canonical action-item files should preserve the metadata needed by later retrieval and distillation."""
    thread_path = _create_thread(tmp_path)
    frontmatter, body = load_markdown(thread_path)
    body = body.replace(
        "Summary pending. [sources: ]",
        "Billy investigated robot connectivity and needs a follow-up. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
    )
    body = body.replace("No open questions yet.", "- Did the retest fix the dropout issue?")
    body = body.replace("No candidate action items yet.", "- Retest robot connectivity tomorrow.")
    write_markdown(thread_path, frontmatter, body)

    sync_thread_state(
        thread_path=str(thread_path),
        workspace_root=str(tmp_path),
        canonical_action_items=[
            {
                "kind": "task",
                "title": "Retest robot connectivity tomorrow",
                "summary_markdown": "Retest robot connectivity tomorrow. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "current_state_markdown": "Open and awaiting execution.",
                "evidence_markdown": "Captured from the thread summary and snippet evidence. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "priority": "high",
                "confidence": "explicit",
                "owner_topic_refs": ["top-people-billy"],
                "linked_topic_refs": ["top-systems-rover-3"],
            }
        ],
    )

    action_item_path = next((tmp_path / "memory" / "action-items" / "open").rglob("*.md"))
    frontmatter, body = load_markdown(action_item_path)
    assert frontmatter["doc_type"] == "action-item"
    assert frontmatter["kind"] == "task"
    assert frontmatter["status"] == "open"
    assert frontmatter["priority"] == "high"
    assert frontmatter["confidence"] == "explicit"
    assert "top-people-billy" in frontmatter["owner_topic_refs"]
    assert "top-systems-rover-3" in frontmatter["linked_topic_refs"]
    assert frontmatter["source_thread_refs"] == ["thr-2026-03-27-robot-debugging"]
    assert frontmatter["preview"]
    assert "## Summary" in body
    assert "## Current State" in body
    assert "## Evidence" in body


def test_list_action_items_filters_by_kind_and_owner(tmp_path: Path) -> None:
    """Intent: structured action-item listing should support the core filtering model promised by the spec."""
    thread_path = _create_thread(tmp_path)
    frontmatter, body = load_markdown(thread_path)
    body = body.replace(
        "Summary pending. [sources: ]",
        "Billy investigated robot connectivity and needs a follow-up. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
    )
    body = body.replace("No open questions yet.", "- Did the retest fix the dropout issue?")
    body = body.replace("No candidate action items yet.", "- Retest robot connectivity tomorrow.")
    write_markdown(thread_path, frontmatter, body)

    sync_thread_state(
        thread_path=str(thread_path),
        workspace_root=str(tmp_path),
        canonical_action_items=[
            {
                "kind": "task",
                "title": "Retest robot connectivity tomorrow",
                "summary_markdown": "Retest robot connectivity tomorrow. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "current_state_markdown": "Open and awaiting execution.",
                "evidence_markdown": "Captured from the thread summary and snippet evidence. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "priority": "high",
                "confidence": "explicit",
                "owner_topic_refs": ["top-people-billy"],
                "linked_topic_refs": ["top-systems-rover-3"],
            },
            {
                "kind": "question",
                "title": "Did the retest fix the dropout issue?",
                "summary_markdown": "Need to confirm whether the retest fixed the dropout issue. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "current_state_markdown": "Open pending retest results.",
                "evidence_markdown": "Derived from the unresolved question in the thread. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
                "confidence": "explicit",
                "linked_topic_refs": ["top-systems-rover-3"],
            },
        ],
    )

    tasks = list_action_items(workspace_root=str(tmp_path), kind="task", owner="top-people-billy")
    questions = list_action_items(workspace_root=str(tmp_path), kind="question")

    assert tasks["total"] == 1
    assert tasks["items"][0]["title"] == "Retest robot connectivity tomorrow"
    assert questions["total"] == 1
    assert questions["items"][0]["title"] == "Did the retest fix the dropout issue?"
