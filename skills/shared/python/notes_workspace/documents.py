"""Document rendering and parsing helpers."""

from __future__ import annotations

import re
from pathlib import Path

from .errors import WorkspaceError

THREAD_BODY_RE = re.compile(
    r"^# (?P<title>.+?)\n\n<!-- BEGIN AUTO -->\n"
    r"## Current Summary\n(?P<summary>.*?)\n\n"
    r"## Open Questions\n(?P<open_questions>.*?)\n\n"
    r"## Candidate Action Items\n(?P<candidate_action_items>.*?)\n\n"
    r"## Distillation Notes\n(?P<distillation_notes>.*?)\n\n"
    r"## Snippets\n(?P<snippets>.*?)\n<!-- END AUTO -->\n?$",
    re.DOTALL,
)

ACTION_ITEM_BODY_RE = re.compile(
    r"^# (?P<title>.+?)\n\n<!-- BEGIN AUTO -->\n"
    r"## Summary\n(?P<summary>.*?)\n\n"
    r"## Current State\n(?P<current_state>.*?)\n\n"
    r"## Evidence\n(?P<evidence>.*?)\n\n"
    r"## Resolution History\n(?P<resolution_history>.*?)\n<!-- END AUTO -->"
    r"(?:\n\n## Manual Notes\n(?P<manual_notes>.*?))?\n?$",
    re.DOTALL,
)


def placeholder(text: str) -> str:
    return text


def preview_from_text(text: str, fallback: str) -> str:
    stripped = re.sub(r"\[sources:[^\]]+\]", "", text).strip()
    stripped = re.sub(r"\s+", " ", stripped)
    if not stripped or stripped.lower().startswith("no "):
        stripped = fallback
    return stripped[:240]


def render_thread_body(
    *,
    title: str,
    summary: str,
    open_questions: str,
    candidate_action_items: str,
    distillation_notes: str,
    snippets: str,
) -> str:
    return (
        f"# {title}\n\n"
        "<!-- BEGIN AUTO -->\n"
        "## Current Summary\n"
        f"{summary.strip()}\n\n"
        "## Open Questions\n"
        f"{open_questions.strip()}\n\n"
        "## Candidate Action Items\n"
        f"{candidate_action_items.strip()}\n\n"
        "## Distillation Notes\n"
        f"{distillation_notes.strip()}\n\n"
        "## Snippets\n"
        f"{snippets.rstrip()}\n"
        "<!-- END AUTO -->\n"
    )


def parse_thread_body(body: str) -> dict[str, str]:
    match = THREAD_BODY_RE.match(body.strip() + "\n")
    if not match:
        raise WorkspaceError(
            "invalid_thread_document",
            "Thread document body does not match the required structure.",
            "Rebuild the thread document using the workspace tooling.",
        )
    return {key: value.rstrip() for key, value in match.groupdict().items()}


def render_snippet(*, snippet_id: str, timestamp: str, body: str, speaker: str | None) -> str:
    lines = [f"### {snippet_id} | {timestamp}", f"- speaker: {speaker}" if speaker else "- speaker: <omitted>", "- kind: note", "- distill_status: pending", "", body.rstrip()]
    return "\n".join(lines).rstrip()


def next_snippet_id(snippets: str) -> str:
    matches = re.findall(r"^### (snp-(\d{4})) \|", snippets, re.MULTILINE)
    if not matches:
        return "snp-0001"
    last_number = max(int(number) for _, number in matches)
    return f"snp-{last_number + 1:04d}"


def render_generated_doc(*, title: str, sections: list[tuple[str, str]]) -> str:
    lines = [f"# {title}", "", "<!-- BEGIN AUTO -->"]
    for heading, content in sections:
        lines.extend([heading, content.strip(), ""])
    lines.append("<!-- END AUTO -->")
    return "\n".join(lines).rstrip() + "\n"


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def render_action_item_body(
    *,
    title: str,
    summary: str,
    current_state: str,
    evidence: str,
    resolution_history: str,
    manual_notes: str = "",
) -> str:
    body = (
        f"# {title}\n\n"
        "<!-- BEGIN AUTO -->\n"
        "## Summary\n"
        f"{summary.strip()}\n\n"
        "## Current State\n"
        f"{current_state.strip()}\n\n"
        "## Evidence\n"
        f"{evidence.strip()}\n\n"
        "## Resolution History\n"
        f"{resolution_history.strip()}\n"
        "<!-- END AUTO -->"
    )
    if manual_notes or manual_notes == "":
        body += f"\n\n## Manual Notes\n{manual_notes.strip()}\n"
    return body


def parse_action_item_body(body: str) -> dict[str, str]:
    match = ACTION_ITEM_BODY_RE.match(body.strip() + "\n")
    if not match:
        raise WorkspaceError(
            "invalid_action_item_document",
            "Action-item document body does not match the required structure.",
            "Rebuild the action-item document using the workspace tooling.",
        )
    parsed = {key: (value or "").rstrip() for key, value in match.groupdict().items()}
    parsed.setdefault("manual_notes", "")
    return parsed
