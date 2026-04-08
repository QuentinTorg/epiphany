---
name: querying-notes
description: Use this skill when the user asks questions about stored notes, action items, people, projects, systems, or prior decisions in the workspace. It teaches progressive-disclosure retrieval and uses coarse query tools to narrow candidate files before the agent synthesizes the answer.
compatibility: Requires Python 3 and a readable note-taking workspace with generated views and canonical records.
metadata:
  owner: epiphany
---

# Querying Notes

Use the tools here to narrow the search space. Do the actual reasoning yourself.

Read [../shared/references/workspace-navigation.md](../shared/references/workspace-navigation.md) before starting.
Read [../shared/references/recovery-policy.md](../shared/references/recovery-policy.md) when pending distillation may affect answer completeness.
Read [references/retrieval-checklist.md](references/retrieval-checklist.md) for the exact retrieval order.
Read [references/query-escalation.md](references/query-escalation.md) when deciding how far to drill into evidence.
Read [references/answer-style.md](references/answer-style.md) before drafting the final answer.
Read [../shared/references/citation-rules.md](../shared/references/citation-rules.md) before drafting the final answer.

## Available scripts

- [scripts/query_memory.py](scripts/query_memory.py) — coarse retrieval across views, threads, topics, imports, and action items
- [scripts/list_action_items.py](scripts/list_action_items.py) — structured filtering over canonical tasks and questions

## Checklist

- start from `memory/README.md`
- narrow with views and query tools before opening many files
- synthesize the answer yourself
- cite raw evidence
- mention pending-distillation uncertainty when relevant

## Workflow

1. Start from `memory/README.md`.
2. If the workspace is not initialized yet, stop and bootstrap it with `python ../shared/scripts/bootstrap_workspace.py ...` before querying.
3. Run `python scripts/query_memory.py --query ...` when the question spans multiple files or needs structured narrowing.
4. Open the most likely candidates returned by the script.
5. Use `python scripts/list_action_items.py ...` when the query is clearly about tasks, blockers, or open questions.
6. Synthesize the answer yourself and cite raw evidence.

## Validation Loop

- Check whether `query_memory.py` returned pending-distillation warnings.
- If warnings exist, reflect that uncertainty in the answer.
- Confirm the final answer cites thread snippets or normalized import text chunks, not only generated summaries.

## Gotchas

- `query_memory.py` is a narrowing tool, not an answer engine.
- Start broad with views and indexes before drilling into thread snippets or normalized import text.
- Do not mutate the workspace from this skill.
- Only call wrappers in `scripts/` or `../shared/scripts/`. Do not treat shared Python modules as normal entrypoints.
