# Script Invocations

Use these command shapes for deep distillation and recovery workflows.

## `resume_pending.py`

Use this when the user asks to recover pending work or review what still needs reconciliation.

Common forms:

```bash
python scripts/resume_pending.py --all
```

If future filters exist, use them only to narrow an already clear recovery target.

Use `--all` as the normal recovery-review mode.

Use `--thread-slug` or `--import-slug` only when the recovery target is already known and you are intentionally narrowing the recovery queue.

Use `--dry-run` only when you want to confirm what the recovery queue contains without treating the call as an actual recovery step.

Use `--workspace-root` only when the current working directory is not already the target workspace root.

## `apply_distillation_result.py`

Always provide:

- one explicit source selector:
  - `--thread-path`, or
  - `--import-record-path`

Use only when needed:

- `--update-json`
- `--close-thread`
- `--rebuild-views`
- `--dry-run`
- `--workspace-root`

Examples:

```bash
python scripts/apply_distillation_result.py \
  --thread-path memory/threads/open/2026/2026-04-08-robot-debugging.md \
  --update-json @distill-update.json
```

```bash
python scripts/apply_distillation_result.py \
  --thread-path memory/threads/open/2026/2026-04-08-robot-debugging.md \
  --update-json @distill-update.json \
  --close-thread
```

Prefer explicit file paths over slug lookup when the exact source file is already known.

Pass `--update-json` when you are applying actual source, topic, or action-item mutations.

Use `--close-thread` only during an explicit close-thread workflow.

Use `--rebuild-views` only when the workflow explicitly calls for it beyond the normal apply behavior.

Use `--dry-run` only for preview or verification.

Use `--workspace-root` only when the current working directory is not already the target workspace root.
