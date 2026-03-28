from __future__ import annotations

from pathlib import Path

from notes_workspace.bootstrap import bootstrap_workspace
from notes_workspace.frontmatter import load_markdown, write_markdown
from notes_workspace.query import query_memory
from notes_workspace.threads import capture_note, sync_thread_state


def _seed_query_workspace(tmp_path: Path) -> dict[str, str]:
    bootstrap_workspace(workspace_root=str(tmp_path))

    first = capture_note(
        thread_slug="robot-debugging",
        thread_title="Robot Debugging",
        stdin_body="Billy investigated the connectivity issue.",
        timestamp="2026-03-27T09:00:00Z",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )
    first_thread_path = tmp_path / first["thread_path"]
    first_frontmatter, first_body = load_markdown(first_thread_path)
    first_body = first_body.replace(
        "Summary pending. [sources: ]",
        f"Billy investigated robot connectivity and needs to retest tomorrow. [sources: {first['thread_id']}#snp-0001]",
    )
    first_body = first_body.replace("No open questions yet.", "- Did the retest fix the dropout issue?")
    first_body = first_body.replace("No candidate action items yet.", "- Retest robot connectivity tomorrow.")
    write_markdown(first_thread_path, first_frontmatter, first_body)
    sync_thread_state(
        thread_path=str(first_thread_path),
        workspace_root=str(tmp_path),
        canonical_action_items=[
            {
                "kind": "task",
                "title": "Retest robot connectivity tomorrow",
                "summary_markdown": f"Retest robot connectivity tomorrow. [sources: {first['thread_id']}#snp-0001]",
                "current_state_markdown": "Open and awaiting execution.",
                "evidence_markdown": f"Captured from thread evidence. [sources: {first['thread_id']}#snp-0001]",
                "priority": "high",
                "confidence": "explicit",
                "owner_topic_refs": ["top-people-billy"],
                "linked_topic_refs": ["top-systems-rover-3"],
            }
        ],
    )

    second = capture_note(
        thread_slug="weekly-status",
        thread_title="Weekly Status",
        stdin_body="Julian prepared the vendor update.",
        timestamp="2026-03-20T09:00:00Z",
        create_if_missing=True,
        workspace_root=str(tmp_path),
    )
    second_thread_path = tmp_path / second["thread_path"]
    second_frontmatter, second_body = load_markdown(second_thread_path)
    second_body = second_body.replace(
        "Summary pending. [sources: ]",
        f"Julian prepared the vendor update for Acme. [sources: {second['thread_id']}#snp-0001]",
    )
    write_markdown(second_thread_path, second_frontmatter, second_body)
    sync_thread_state(thread_path=str(second_thread_path), workspace_root=str(tmp_path))

    return {
        "first_thread_id": first["thread_id"],
        "first_thread_path": first["thread_path"],
        "second_thread_id": second["thread_id"],
        "second_thread_path": second["thread_path"],
    }


def test_query_memory_returns_coarse_candidates_for_agent_review(tmp_path: Path) -> None:
    """Intent: query helper should narrow the search space to relevant candidate files, not synthesize the final answer."""
    _seed_query_workspace(tmp_path)

    result = query_memory(query="What is Billy working on?", workspace_root=str(tmp_path))

    assert "memory/README.md" in result["recommended_start_paths"]
    assert result["candidates"]
    paths = [candidate["path"] for candidate in result["candidates"]]
    assert any(path.endswith("robot-debugging.md") for path in paths)
    assert any("action-items/open/" in path for path in paths)
    assert paths[0].endswith("robot-debugging.md")
    assert "action-items/open/" in paths[1]
    assert all(candidate["excerpt"] for candidate in result["candidates"])


def test_query_memory_filters_by_entity_and_date_range(tmp_path: Path) -> None:
    """Intent: query helper should honor structured narrowing filters before the agent opens full documents."""
    _seed_query_workspace(tmp_path)

    result = query_memory(
        query="vendor update",
        workspace_root=str(tmp_path),
        date_to="2026-03-21T00:00:00Z",
    )

    paths = [candidate["path"] for candidate in result["candidates"]]
    assert any(path.endswith("weekly-status.md") for path in paths)
    assert not any(path.endswith("robot-debugging.md") for path in paths)


def test_query_memory_warns_when_pending_distillation_may_affect_results(tmp_path: Path) -> None:
    """Intent: query helper should surface pending-distillation risk instead of silently pretending the workspace is fully reconciled."""
    seeded = _seed_query_workspace(tmp_path)

    result = query_memory(
        query="robot connectivity retest",
        workspace_root=str(tmp_path),
        source_thread=seeded["first_thread_id"],
    )

    assert result["pending_warnings"]
    assert "Robot Debugging" in result["pending_warnings"][0]
