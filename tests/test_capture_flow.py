from __future__ import annotations

import json
from pathlib import Path

from notes_workspace.bootstrap import bootstrap_workspace
from notes_workspace.frontmatter import load_markdown
from notes_workspace.threads import apply_thread_update, capture_note, get_thread_status


def test_capture_note_creates_thread_and_updates_views(tmp_path: Path) -> None:
    """Intent: first note capture should create a thread and refresh the open-thread surfaces."""
    bootstrap_workspace(workspace_root=str(tmp_path))

    result = capture_note(
        thread_slug="robot-debugging",
        thread_title="Robot Debugging",
        stdin_body="Billy investigated the connectivity issue.",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )

    thread_path = tmp_path / result["thread_path"]
    assert thread_path.exists()
    assert (tmp_path / "memory" / "views" / "open-threads.md").exists()

    frontmatter, body = load_markdown(thread_path)
    assert frontmatter["thread_status"] == "open"
    assert frontmatter["distillation_state"] == "pending"
    assert "Billy investigated the connectivity issue." in body

    open_threads_view = (tmp_path / "memory" / "views" / "open-threads.md").read_text(encoding="utf-8")
    assert "Open question count: 0" in open_threads_view


def test_apply_thread_update_refreshes_summary_and_status(tmp_path: Path) -> None:
    """Intent: agent-authored thread-local updates should refresh summary-derived status fields."""
    bootstrap_workspace(workspace_root=str(tmp_path))
    capture = capture_note(
        thread_slug="robot-debugging",
        thread_title="Robot Debugging",
        stdin_body="Billy investigated the connectivity issue.",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )
    thread_path = str(tmp_path / capture["thread_path"])

    apply_thread_update(
        thread_path=thread_path,
        update_json=json.dumps(
            {
                "summary_markdown": "Billy investigated robot connectivity and needs to retest tomorrow. [sources: thr-2026-01-01-robot-debugging#snp-0001]",
                "open_questions_markdown": "- Did the retest fix the dropout issue?",
                "candidate_action_items_markdown": "- Retest robot connectivity tomorrow.",
                "distillation_notes_markdown": "Lightweight distillation completed for the current snippet.",
                "primary_topic_refs": ["top-systems-rover-3"],
                "primary_entity_refs": ["top-people-billy"],
            }
        ),
        workspace_root=str(tmp_path),
    )

    status = get_thread_status(thread_path=thread_path, workspace_root=str(tmp_path))
    assert "retest tomorrow" in status["preview"].lower()
    assert status["snippet_count"] == 1
    assert status["primary_topic_refs"] == ["top-systems-rover-3"]
    assert status["primary_entity_refs"] == ["top-people-billy"]

    open_threads_view = (tmp_path / "memory" / "views" / "open-threads.md").read_text(encoding="utf-8")
    pending_view = (tmp_path / "memory" / "views" / "pending-distillation.md").read_text(encoding="utf-8")
    assert "Open question count: 1" in open_threads_view
    assert "| state `open` |" in pending_view
