---
name: querying-notes
description: Use this skill when the user asks questions about stored notes, action items, people, projects, systems, or prior decisions in the workspace. It teaches progressive-disclosure retrieval and uses coarse query tools to narrow candidate files before the agent synthesizes the answer.
compatibility: Requires Python 3 and a readable note-taking workspace with generated views and canonical records.
metadata:
  owner: epiphany
---

# Querying Notes

Use the tools here to narrow the search space. Do the actual reasoning yourself.

Read `../shared/references/workspace-navigation.md` before starting.
Read `references/retrieval-checklist.md` for the exact retrieval order.
Read `../shared/references/citation-rules.md` before drafting the final answer.

## Available scripts

- `scripts/query_memory.py` — coarse retrieval across views, threads, topics, imports, and action items
- `scripts/list_action_items.py` — structured filtering over canonical tasks and questions

## Checklist

- start from `memory/README.md`
- narrow with views and query tools before opening many files
- synthesize the answer yourself
- cite raw evidence
- mention pending-distillation uncertainty when relevant

## Workflow

1. Start from `memory/README.md`.
2. Run `python scripts/query_memory.py --query ...` when the question spans multiple files or needs structured narrowing.
3. Open the most likely candidates returned by the script.
4. Use `python scripts/list_action_items.py ...` when the query is clearly about tasks, blockers, or open questions.
5. Synthesize the answer yourself and cite raw evidence.

## Validation Loop

- Check whether `query_memory.py` returned pending-distillation warnings.
- If warnings exist, reflect that uncertainty in the answer.
- Confirm the final answer cites thread snippets or normalized import text chunks, not only generated summaries.

## Gotchas

- `query_memory.py` is a narrowing tool, not an answer engine.
- Start broad with views and indexes before drilling into thread snippets or normalized import text.
- Do not mutate the workspace from this skill.
