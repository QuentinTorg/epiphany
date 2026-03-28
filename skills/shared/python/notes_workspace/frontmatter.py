"""Minimal YAML-frontmatter helpers for predictable generated docs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import WorkspaceError


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw == "":
        return ""
    if raw.startswith('"') or raw in {"true", "false", "null"}:
        return json.loads(raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def parse_frontmatter_text(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise WorkspaceError(
            "invalid_frontmatter",
            "Document is missing YAML frontmatter.",
            "Rebuild the file using the workspace tooling.",
        )

    try:
        _, remainder = text.split("---\n", 1)
        fm_text, body = remainder.split("---\n", 1)
    except ValueError as exc:
        raise WorkspaceError(
            "invalid_frontmatter",
            "Document frontmatter is not terminated correctly.",
            "Rebuild the file using the workspace tooling.",
        ) from exc

    data: dict[str, Any] = {}
    lines = fm_text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if ":" not in line:
            raise WorkspaceError(
                "invalid_frontmatter",
                f"Invalid frontmatter line: {line!r}",
                "Rebuild the file using the workspace tooling.",
            )
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            items: list[Any] = []
            index += 1
            while index < len(lines) and lines[index].startswith("  - "):
                items.append(_parse_scalar(lines[index][4:]))
                index += 1
            data[key] = items
            continue
        data[key] = _parse_scalar(value)
        index += 1

    return data, body.lstrip("\n")


def load_markdown(path: Path) -> tuple[dict[str, Any], str]:
    return parse_frontmatter_text(path.read_text(encoding="utf-8"))


def _format_scalar(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value)
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return json.dumps(value)
    raise TypeError(f"Unsupported frontmatter scalar type: {type(value)!r}")


def dump_frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
                continue
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {_format_scalar(item)}")
            continue
        lines.append(f"{key}: {_format_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def write_markdown(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    text = f"{dump_frontmatter(frontmatter)}\n\n{body.rstrip()}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
