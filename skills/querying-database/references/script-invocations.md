# Script Invocations

Use these command shapes for normal query workflows.

## `query_memory.py`

Always provide:

- `--query`

Use only when the user request clearly supports them:

- `--mode concise|research`
- `--topic`
- `--entity`
- `--date-from`
- `--date-to`
- `--source-thread`
- `--source-import`
- `--limit`
- `--offset`
- `--output-file`
- `--workspace-root`

Examples:

```bash
python scripts/query_memory.py \
  --query "What is Billy working on?"
```

```bash
python scripts/query_memory.py \
  --query "What did Billy work on last week?" \
  --entity "Billy" \
  --date-from 2026-04-01 \
  --date-to 2026-04-07
```

Use this script to narrow candidates, not to answer the question directly.

Use `--mode research` only when the user wants a broader or deeper investigation than the default concise retrieval pass.

Use `--topic`, `--entity`, `--date-from`, and `--date-to` only when the question clearly narrows on those axes.

Use `--limit`, `--offset`, and `--output-file` only when the candidate set is large enough to require paging or file output.

Use `--workspace-root` only when the current working directory is not already the target workspace root.

## `list_action_items.py`

Use this when the question is clearly about tasks, blockers, or unresolved questions.

Common useful filters:

- `--kind`
- `--status`
- `--owner`
- `--topic`
- `--entity`
- `--date-from`
- `--date-to`
- `--source-thread`
- `--source-import`

Use only when needed:

- `--include-closed`
- `--limit`
- `--offset`
- `--output-file`
- `--workspace-root`

Prefer coarse filtering first, then open the returned records yourself.

Use `--owner` when the question is about the person who owns the work.

Use `--topic` when the question is scoped to one canonical topic.

Use `--entity` when the user names a person, project, or other entity but the exact canonical topic linkage may not be known yet.

Use `--include-closed` only when historical done or resolved items are relevant to the question.

Use `--limit`, `--offset`, and `--output-file` only for large result sets or downstream processing.

Use `--workspace-root` only when the current working directory is not already the target workspace root.
