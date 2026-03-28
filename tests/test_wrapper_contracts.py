from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _parse_json_stdout(completed: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert completed.stdout, completed.stderr
    return json.loads(completed.stdout)


def test_bootstrap_wrapper_emits_common_json_envelope(tmp_path: Path) -> None:
    """Intent: bootstrap wrapper should follow the common stdout envelope contract."""
    completed = _run(
        [
            "skills/shared/scripts/bootstrap_workspace.py",
            "--workspace-root",
            str(tmp_path),
        ]
    )

    assert completed.returncode == 0, completed.stderr
    payload = _parse_json_stdout(completed)
    assert payload["ok"] is True
    assert payload["error"] is None
    assert payload["workspace_root"] == str(tmp_path.resolve())
    assert isinstance(payload["warnings"], list)
    assert isinstance(payload["paths_created"], list)
    assert isinstance(payload["paths_updated"], list)
    assert isinstance(payload["result"], dict)


def test_capture_wrapper_dry_run_does_not_create_thread_file(tmp_path: Path) -> None:
    """Intent: capture wrapper dry-run should avoid durable note creation."""
    _run(["skills/shared/scripts/bootstrap_workspace.py", "--workspace-root", str(tmp_path)])

    completed = _run(
        [
            "skills/capturing-notes/scripts/capture_note.py",
            "--workspace-root",
            str(tmp_path),
            "--thread-slug",
            "robot-debugging",
            "--thread-title",
            "Robot Debugging",
            "--create-if-missing",
            "--stdin-body",
            "Billy investigated the connectivity issue.",
            "--dry-run",
        ]
    )

    assert completed.returncode == 0, completed.stderr
    payload = _parse_json_stdout(completed)
    assert payload["ok"] is True
    assert not list((tmp_path / "memory" / "threads" / "open").rglob("*.md"))


def test_capture_wrapper_returns_actionable_error_for_missing_thread_title(tmp_path: Path) -> None:
    """Intent: capture wrapper should return a structured actionable error for invalid create-if-missing input."""
    _run(["skills/shared/scripts/bootstrap_workspace.py", "--workspace-root", str(tmp_path)])

    completed = _run(
        [
            "skills/capturing-notes/scripts/capture_note.py",
            "--workspace-root",
            str(tmp_path),
            "--thread-slug",
            "robot-debugging",
            "--create-if-missing",
            "--stdin-body",
            "Billy investigated the connectivity issue.",
        ]
    )

    assert completed.returncode == 2
    payload = _parse_json_stdout(completed)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "missing_thread_title"
    assert payload["error"]["hint"]


def test_sync_thread_state_wrapper_returns_structured_error_for_invalid_action_item_json(tmp_path: Path) -> None:
    """Intent: sync-thread-state wrapper should reject malformed canonical action-item payloads with a structured error."""
    _run(["skills/shared/scripts/bootstrap_workspace.py", "--workspace-root", str(tmp_path)])
    capture = _parse_json_stdout(
        _run(
            [
                "skills/capturing-notes/scripts/capture_note.py",
                "--workspace-root",
                str(tmp_path),
                "--thread-slug",
                "robot-debugging",
                "--thread-title",
                "Robot Debugging",
                "--create-if-missing",
                "--stdin-body",
                "Billy investigated the connectivity issue.",
            ]
        )
    )
    thread_path = str(tmp_path / capture["result"]["thread_path"])

    completed = _run(
        [
            "skills/capturing-notes/scripts/sync_thread_state.py",
            "--workspace-root",
            str(tmp_path),
            "--thread-path",
            thread_path,
            "--canonical-action-items-json",
            "{not-json}",
        ]
    )

    assert completed.returncode == 2
    payload = _parse_json_stdout(completed)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "invalid_canonical_action_items_json"


def test_thread_status_wrapper_reports_current_thread_state(tmp_path: Path) -> None:
    """Intent: thread-status wrapper should expose the current thread status using the common JSON envelope."""
    _run(["skills/shared/scripts/bootstrap_workspace.py", "--workspace-root", str(tmp_path)])
    _run(
        [
            "skills/capturing-notes/scripts/capture_note.py",
            "--workspace-root",
            str(tmp_path),
            "--thread-slug",
            "robot-debugging",
            "--thread-title",
            "Robot Debugging",
            "--create-if-missing",
            "--stdin-body",
            "Billy investigated the connectivity issue.",
        ]
    )

    completed = _run(
        [
            "skills/capturing-notes/scripts/thread_status.py",
            "--workspace-root",
            str(tmp_path),
            "--thread-slug",
            "robot-debugging",
        ]
    )

    assert completed.returncode == 0, completed.stderr
    payload = _parse_json_stdout(completed)
    assert payload["ok"] is True
    assert payload["result"]["thread_status"] == "open"
    assert payload["result"]["distillation_state"] == "pending"


def test_sync_thread_state_wrapper_refreshes_preview_after_direct_edit(tmp_path: Path) -> None:
    """Intent: sync-thread-state wrapper should support the direct-edit workflow by refreshing metadata and views."""
    _run(["skills/shared/scripts/bootstrap_workspace.py", "--workspace-root", str(tmp_path)])
    capture = _parse_json_stdout(
        _run(
            [
                "skills/capturing-notes/scripts/capture_note.py",
                "--workspace-root",
                str(tmp_path),
                "--thread-slug",
                "robot-debugging",
                "--thread-title",
                "Robot Debugging",
                "--create-if-missing",
                "--stdin-body",
                "Billy investigated the connectivity issue.",
            ]
        )
    )
    thread_path = tmp_path / capture["result"]["thread_path"]
    contents = thread_path.read_text(encoding="utf-8")
    contents = contents.replace(
        "Summary pending. [sources: ]",
        "Billy investigated robot connectivity and needs to retest tomorrow. [sources: thr-2026-03-27-robot-debugging#snp-0001]",
    )
    thread_path.write_text(contents, encoding="utf-8")

    completed = _run(
        [
            "skills/capturing-notes/scripts/sync_thread_state.py",
            "--workspace-root",
            str(tmp_path),
            "--thread-path",
            str(thread_path),
        ]
    )

    assert completed.returncode == 0, completed.stderr
    payload = _parse_json_stdout(completed)
    assert payload["ok"] is True
    assert payload["result"]["thread_path"].endswith("robot-debugging.md")
    refreshed = thread_path.read_text(encoding="utf-8")
    assert 'preview: "Billy investigated robot connectivity and needs to retest tomorrow."' in refreshed
