# Script Invocations

Use these command shapes for normal capture workflows.

## `capture_note.py`

Preferred cases:

- existing known thread:
  - use `--thread-path`
- start a new thread:
  - use `--thread-title`
  - add `--create-if-missing`

Always provide:

- `--stdin-body`

Use only when needed:

- `--speaker`
- `--timestamp`
- `--workspace-root`
- `--dry-run`

Normal capture should omit `--timestamp`.

The script should stamp the current time internally during standard note capture.

Use `--timestamp` only when the captured note must be recorded with a time other than the current time, such as backfilling older notes or preserving an externally known event time.

Use `--workspace-root` only when the current working directory is not already the target workspace root.

Use `--dry-run` only to preview or verify the operation without making durable changes.

Examples:

```bash
python scripts/capture_note.py \
  --thread-path memory/threads/open/2026/2026-04-08-robot-debugging.md \
  --stdin-body "Billy debugged the CAN bus issue and will retest Friday."
```

```bash
python scripts/capture_note.py \
  --thread-title "Robot Debugging" \
  --create-if-missing \
  --stdin-body "Started a new debugging session for Rover 3."
```

Prefer `--thread-path` over `--thread-slug` when the exact thread file is already known.

Use `--thread-slug` only when the exact thread path is not already known.

Use `--thread-title` with `--create-if-missing` only when intentionally starting a new thread.

## `sync_thread_state.py`

Always provide:

- `--thread-path`

Use only when needed:

- `--canonical-action-items-json`
- `--workspace-root`
- `--dry-run`

Example:

```bash
python scripts/sync_thread_state.py \
  --thread-path memory/threads/open/2026/2026-04-08-robot-debugging.md
```

Pass `--canonical-action-items-json` only when you already prepared explicit canonical action-item payloads.

Use `--workspace-root` only when the current working directory is not already the target workspace root.

Use `--dry-run` only for preview or verification.

## `thread_status.py`

Use this after sync to confirm current thread state.

Prefer:

- `--thread-path`

Use slug lookup only when the exact file path is not already known.

Use `--workspace-root` only when the current working directory is not already the target workspace root.
