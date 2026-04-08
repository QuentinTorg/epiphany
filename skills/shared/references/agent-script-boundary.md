# Agent-Script Boundary

Use this project with one strict rule:

- agents do semantic work
- scripts do mechanical work

Semantic work:

- writing summaries
- deciding which topics are affected
- deciding which action items or open questions exist
- deciding how evidence changes current understanding
- synthesizing answers for the user

Mechanical work:

- creating files
- appending raw evidence
- stamping timestamps
- maintaining frontmatter
- validating document structure
- moving files between lifecycle locations
- rebuilding generated views and indexes
- applying already-authored structured results

Do not ask a script to figure out what a summary should say.
Do not ask a script to decide how a topic changes.

Use scripts after semantic edits to keep the workspace structurally consistent.

## Callable script surface

Only these locations are part of the normal callable tool surface:

- `skills/*/scripts/*.py`
- `skills/shared/scripts/*.py`

Treat these as internal implementation modules, not normal direct entrypoints:

- `skills/shared/python/notes_workspace/*.py`

The internal modules exist to support the wrapper scripts. Do not call them directly unless a future skill explicitly says to do so.

## Common argument defaults

Use these defaults unless a skill-specific reference says otherwise:

- omit `--workspace-root` when the current working directory is already the target workspace root
- prefer explicit `--*-path` selectors over slug selectors when the exact file is already known
- use slug selectors only when the exact file path is not already known
- use `--dry-run` only for preview or verification, not for the normal workflow
- use paging or output flags such as `--limit`, `--offset`, or `--output-file` only when the result set is large enough to need them

## Which script to use when

Use these wrappers for these jobs:

- initialize a workspace:
  - [../scripts/bootstrap_workspace.py](../scripts/bootstrap_workspace.py)
- capture raw notes into a thread:
  - [../../capturing-notes/scripts/capture_note.py](../../capturing-notes/scripts/capture_note.py)
- refresh thread metadata and mechanical views after direct thread edits:
  - [../../capturing-notes/scripts/sync_thread_state.py](../../capturing-notes/scripts/sync_thread_state.py)
- inspect current thread state:
  - [../../capturing-notes/scripts/thread_status.py](../../capturing-notes/scripts/thread_status.py)
- narrow the search space for broad questions:
  - [../../querying-notes/scripts/query_memory.py](../../querying-notes/scripts/query_memory.py)
- filter canonical tasks and open questions:
  - [../../querying-notes/scripts/list_action_items.py](../../querying-notes/scripts/list_action_items.py)
- review pending reconciliation work:
  - [../../distilling-threads/scripts/resume_pending.py](../../distilling-threads/scripts/resume_pending.py)
- apply an already-authored deep-distillation result:
  - [../../distilling-threads/scripts/apply_distillation_result.py](../../distilling-threads/scripts/apply_distillation_result.py)
- ingest an external document into workspace evidence:
  - [../../ingesting-documents/scripts/ingest_document.py](../../ingesting-documents/scripts/ingest_document.py)
- refresh import-record metadata and mechanical views after direct import-record edits:
  - [../../ingesting-documents/scripts/sync_import_state.py](../../ingesting-documents/scripts/sync_import_state.py)

## Workflow routing

- user is adding notes or continuing a live session:
  - use `capturing-notes`
- user is asking questions about the stored workspace:
  - use `querying-notes`
- user wants to reconcile, recover pending work, bubble knowledge into topics/action items, or close a thread:
  - use `distilling-threads`
- user wants to bring an external source document into the workspace:
  - use `ingesting-documents`

## Cross-skill handoffs

- If capture work becomes explicit thread closing or deep reconciliation, hand off from `capturing-notes` to `distilling-threads`.
- If document ingestion should be fully reconciled immediately, hand off from `ingesting-documents` to `distilling-threads` after syncing the import record.
- If a query reveals the answer is blocked by pending distillation, say so and recommend or perform the `distilling-threads` workflow when appropriate.

## Bootstrap rule

If the workspace does not yet contain the expected `memory/` layout, bootstrap it first with:

- [../scripts/bootstrap_workspace.py](../scripts/bootstrap_workspace.py)

Do this before capture, query, distillation, or ingestion work.
