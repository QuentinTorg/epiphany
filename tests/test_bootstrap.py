from __future__ import annotations

from notes_workspace.frontmatter import load_markdown
from pathlib import Path

from notes_workspace.bootstrap import bootstrap_workspace


def test_bootstrap_creates_workspace_layout(tmp_path: Path) -> None:
    """Intent: bootstrap should create the required empty workspace layout and seed files."""
    result = bootstrap_workspace(workspace_root=str(tmp_path))

    assert (tmp_path / "memory" / "README.md").exists()
    assert (tmp_path / "memory" / "views" / "open-threads.md").exists()
    assert (tmp_path / "memory" / "views" / "pending-distillation.md").exists()
    assert (tmp_path / "memory" / "topics" / "index.md").exists()
    assert ".gitignore" not in "\n".join(result["updated_paths"])

    readme_frontmatter, readme_body = load_markdown(tmp_path / "memory" / "README.md")
    assert readme_frontmatter["doc_type"] == "workspace-entrypoint"
    assert readme_frontmatter["generated"] is True
    assert readme_frontmatter["preview"]
    assert "<!-- BEGIN AUTO -->" in readme_body

    open_threads_frontmatter, _ = load_markdown(tmp_path / "memory" / "views" / "open-threads.md")
    assert open_threads_frontmatter["doc_type"] == "generated-view"
    assert open_threads_frontmatter["view_type"] == "open-threads"
    assert open_threads_frontmatter["preview"]


def test_bootstrap_updates_gitignore_for_git_workspace(tmp_path: Path) -> None:
    """Intent: bootstrap should keep runtime state out of Git-backed workspaces."""
    (tmp_path / ".git").mkdir()

    bootstrap_workspace(workspace_root=str(tmp_path))

    gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert ".notes-runtime/" in gitignore


def test_bootstrap_dry_run_makes_no_workspace_changes(tmp_path: Path) -> None:
    """Intent: dry-run bootstrap should report safely without creating durable workspace files."""
    result = bootstrap_workspace(workspace_root=str(tmp_path), dry_run=True)

    assert result["created_dirs"] == []
    assert result["updated_paths"] == []
    assert not (tmp_path / "memory").exists()
