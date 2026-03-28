from __future__ import annotations

import json
from pathlib import Path

from notes_workspace.bootstrap import bootstrap_workspace
from notes_workspace.frontmatter import load_markdown, write_markdown
from notes_workspace.threads import capture_note, get_thread_status, sync_thread_state


def test_capture_note_creates_thread_and_updates_views(tmp_path: Path) -> None:
    """Intent: first note capture should create a thread and refresh the open-thread surfaces."""
    bootstrap_workspace(workspace_root=str(tmp_path))

    result = capture_note(
        thread_slug="robot-debugging",
        thread_title="Robot Debugging",
        stdin_body="Billy investigated the connectivity issue.",
        timestamp="2026-03-27T09:00:00Z",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )

    thread_path = tmp_path / result["thread_path"]
    assert thread_path.exists()
    assert (tmp_path / "memory" / "views" / "open-threads.md").exists()

    frontmatter, body = load_markdown(thread_path)
    assert frontmatter["thread_status"] == "open"
    assert frontmatter["distillation_state"] == "pending"
    assert frontmatter["last_captured_at"]
    assert "Billy investigated the connectivity issue." in body

    open_threads_view = (tmp_path / "memory" / "views" / "open-threads.md").read_text(encoding="utf-8")
    assert "Open question count: 0" in open_threads_view


def test_sync_thread_state_refreshes_summary_and_status_after_direct_edit(tmp_path: Path) -> None:
    """Intent: direct thread-local edits should become operationally visible after the structural sync step."""
    bootstrap_workspace(workspace_root=str(tmp_path))
    capture = capture_note(
        thread_slug="robot-debugging",
        thread_title="Robot Debugging",
        stdin_body="Billy investigated the connectivity issue.",
        timestamp="2026-03-27T09:00:00Z",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )
    thread_path = str(tmp_path / capture["thread_path"])

    frontmatter, body = load_markdown(Path(thread_path))
    body = body.replace(
        "Summary pending. [sources: ]",
        "Billy investigated robot connectivity and needs to retest tomorrow. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
    )
    body = body.replace("No open questions yet.", "- Did the retest fix the dropout issue?")
    body = body.replace("No candidate action items yet.", "- Retest robot connectivity tomorrow.")
    write_markdown(Path(thread_path), frontmatter, body)

    sync_thread_state(thread_path=thread_path, workspace_root=str(tmp_path))

    status = get_thread_status(thread_path=thread_path, workspace_root=str(tmp_path))
    assert "retest tomorrow" in status["preview"].lower()
    assert status["snippet_count"] == 1
    assert status["last_captured_at"]

    open_threads_view = (tmp_path / "memory" / "views" / "open-threads.md").read_text(encoding="utf-8")
    pending_view = (tmp_path / "memory" / "views" / "pending-distillation.md").read_text(encoding="utf-8")
    assert "Open question count: 1" in open_threads_view
    assert "| state `open` |" in pending_view


def test_direct_thread_edit_plus_sync_refreshes_metadata_and_views(tmp_path: Path) -> None:
    """Intent: direct agent edits to derived thread prose should be supported via a lightweight structural sync step."""
    bootstrap_workspace(workspace_root=str(tmp_path))
    capture = capture_note(
        thread_slug="robot-debugging",
        thread_title="Robot Debugging",
        stdin_body="Billy investigated the connectivity issue.",
        timestamp="2026-03-27T09:00:00Z",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )
    thread_path = tmp_path / capture["thread_path"]
    frontmatter, body = load_markdown(thread_path)

    body = body.replace(
        "Summary pending. [sources: ]",
        "Billy investigated robot connectivity and needs to retest tomorrow. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
    )
    body = body.replace("No open questions yet.", "- Did the retest fix the dropout issue?")
    body = body.replace("No candidate action items yet.", "- Retest robot connectivity tomorrow.")
    write_markdown(thread_path, frontmatter, body)

    sync_thread_state(thread_path=str(thread_path), workspace_root=str(tmp_path))

    status = get_thread_status(thread_path=str(thread_path), workspace_root=str(tmp_path))
    assert "retest tomorrow" in status["preview"].lower()
    open_threads_view = (tmp_path / "memory" / "views" / "open-threads.md").read_text(encoding="utf-8")
    assert "Open question count: 1" in open_threads_view


def test_stale_open_threads_are_based_on_last_captured_at_not_sync_time(tmp_path: Path) -> None:
    """Intent: stale-open classification should track when the last snippet was captured, not when metadata was last refreshed."""
    bootstrap_workspace(workspace_root=str(tmp_path))
    capture = capture_note(
        thread_slug="weekly-status",
        thread_title="Weekly Status",
        stdin_body="Julian prepared the vendor update.",
        timestamp="2026-03-20T09:00:00Z",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )
    thread_path = tmp_path / capture["thread_path"]
    frontmatter, body = load_markdown(thread_path)
    body = body.replace(
        "Summary pending. [sources: ]",
        "Julian prepared the vendor update for Acme. [sources: thr-2026-03-20-weekly-status#snp-0001]",
    )
    write_markdown(thread_path, frontmatter, body)

    sync_thread_state(thread_path=str(thread_path), workspace_root=str(tmp_path))

    refreshed_frontmatter, _ = load_markdown(thread_path)
    assert refreshed_frontmatter["last_captured_at"] == "2026-03-20T09:00:00Z"
    assert refreshed_frontmatter["last_updated_at"] != refreshed_frontmatter["last_captured_at"]

    open_threads_view = (tmp_path / "memory" / "views" / "open-threads.md").read_text(encoding="utf-8")
    assert "## Active Threads\nNo active open threads." in open_threads_view
    assert "## Stale-Open Threads" in open_threads_view
    assert "Weekly Status" in open_threads_view
    assert "captured `2026-03-20T09:00:00Z`" in open_threads_view
