---
name: distilling-threads
description: Use this skill when the user asks to reconcile notes, bubble thread or import knowledge into canonical topics and action items, recover pending distillation work, or explicitly close a thread. It applies agent-authored deep-distillation results with the distillation scripts and refreshes canonical views.
compatibility: Requires Python 3, a writable workspace root, and the Agentic Notes Workspace layout.
metadata:
  owner: ai-notes-2
---

# Distilling Threads

This skill is for deep reconciliation, not lightweight capture updates.

Read `../shared/references/agent-script-boundary.md` before using this skill.
Read `references/deep-distillation-checklist.md` before preparing a distillation payload.
Read `../shared/references/citation-rules.md` when writing topic or action-item prose.

## Available scripts

- `scripts/apply_distillation_result.py` — apply an already-authored deep-distillation result to a thread or import
- `scripts/resume_pending.py` — list pending distillation work for recovery

## Checklist

- read the source plus linked canonical records
- decide the semantic changes yourself
- prepare the distillation payload
- apply it structurally with the wrapper
- verify state transitions and rebuilt views
- keep the source pending if reconciliation is incomplete

## Workflow

1. Use `python scripts/resume_pending.py --all` when the user asks for recovery or wants to review pending work.
2. Read the source thread or import record plus directly linked topics and action items.
3. Decide the semantic updates yourself:
   - which topics change or should be created
   - which action items change or should be created
   - whether the source can be marked complete or must remain pending
4. Prepare the `--update-json` payload.
5. Run `python scripts/apply_distillation_result.py ...`.
6. If the user explicitly asked to close a thread and distillation succeeded, follow the Git-aware close-thread prompt behavior.

## Validation Loop

- Confirm the source record’s pending/complete state is correct after applying.
- Open the affected topic and action-item documents and verify the expected prose landed there.
- Confirm the relevant topic indexes and generated views were rebuilt.
- If contradictions remain unresolved, keep the source pending and record the reason.

## Gotchas

- `apply_distillation_result.py` does not invent topic summaries or action-item content. You must decide those first.
- Deep distillation may run without closing a thread.
- Do not mark a source complete if unresolved contradictions still block the workspace’s current understanding.
- Only show the Git commit prompt during an explicit close-thread workflow in a Git workspace.
