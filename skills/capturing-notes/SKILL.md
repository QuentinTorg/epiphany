---
name: capturing-notes
description: Use this skill when the user is adding rough notes, continuing an active note-taking session, or asking to append information into a thread. It handles thread selection, raw snippet capture, direct editing of thread-local derived prose, and structural follow-up with the capture and sync scripts.
compatibility: Requires Python 3, a writable workspace root, and the Epiphany workspace layout.
metadata:
  owner: epiphany
---

# Capturing Notes

Capture raw note evidence first. Keep semantic edits agent-authored and use scripts only for structural state.

Read [../shared/references/agent-script-boundary.md](../shared/references/agent-script-boundary.md) before using this skill.
Read [../shared/references/workspace-model.md](../shared/references/workspace-model.md) when you need to decide where captured information belongs.
Read [../shared/references/action-item-policy.md](../shared/references/action-item-policy.md) when notes imply tasks or unresolved questions.
Read [references/thread-selection.md](references/thread-selection.md) when you need to decide whether to append to an existing thread or start a new one.
Read [references/lightweight-distillation.md](references/lightweight-distillation.md) before performing the thread-local synthesis update.
Read [references/capture-edge-cases.md](references/capture-edge-cases.md) when routing or task extraction is ambiguous.
Read [references/script-invocations.md](references/script-invocations.md) before running capture scripts if you need argument guidance.
Read [../shared/references/citation-rules.md](../shared/references/citation-rules.md) if you are writing or revising thread-local summaries.

## Available scripts

- [scripts/capture_note.py](scripts/capture_note.py) — create or append to a thread and add a raw snippet
- [scripts/sync_thread_state.py](scripts/sync_thread_state.py) — refresh thread metadata and mechanical views after direct thread edits
- [scripts/thread_status.py](scripts/thread_status.py) — inspect current thread state

## Checklist

- choose the correct thread or ask if routing is ambiguous
- capture raw evidence first
- edit thread-local prose directly
- sync structural state after the edit
- verify the thread and views reflect the update

## Workflow

1. Start from `memory/README.md` and `memory/views/open-threads.md`.
2. If the workspace is not initialized yet, run `python ../shared/scripts/bootstrap_workspace.py ...` first.
3. Decide whether to append to an existing thread or create a new one.
4. Run `python scripts/capture_note.py ...` to append the raw note.
5. Edit the thread’s `## Current Summary`, `## Open Questions`, `## Candidate Action Items`, and `## Distillation Notes` directly.
6. If the note introduced explicit canonical action items, prepare the structured payload for them.
7. Run `python scripts/sync_thread_state.py ...` to refresh preview, pending state, and views.

## Validation Loop

- Run `python scripts/thread_status.py ...` after syncing.
- Confirm the thread preview matches the current summary.
- Confirm `memory/views/open-threads.md` and `memory/views/pending-distillation.md` reflect the update.
- If you added explicit canonical action items, confirm they appear in `memory/views/action-items.md`.

## Gotchas

- `capture_note.py` does not summarize. It only appends raw evidence and thread metadata.
- In normal capture, do not pass `--timestamp`; let `capture_note.py` stamp the current time internally. Use `--timestamp` only when the note must be recorded with a different time.
- `sync_thread_state.py` does not decide what changed semantically. Edit the thread prose first, then sync.
- Stale-open routing is based on `last_captured_at`, not on later metadata touches.
- Do not close a thread from this skill. Use `distilling-threads` when the user asks to reconcile or close.
- Only call wrappers in `scripts/` or `../shared/scripts/`. Do not treat shared Python modules as normal entrypoints.
