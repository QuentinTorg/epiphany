# Validation Audit

This document records the current validation state after the first end-to-end implementation passes for capture, query, distillation, and document ingestion.

## Manual Workflow Validation

### Capture workflow

- Bootstrapped a workspace.
- Captured rough notes into a thread.
- Edited thread-local prose directly.
- Ran `sync_thread_state.py`.
- Verified `open-threads.md`, `pending-distillation.md`, and `action-items.md` reflected the update.

### Query workflow

- Seeded a workspace with two realistic threads and one canonical action item.
- Queried for:
  - `What is Billy working on?`
  - `vendor update` with a date filter.
- Verified `query_memory.py` returned narrowed candidate paths, small excerpts, and pending-distillation warnings rather than trying to answer semantically.

### Thread distillation workflow

- Deep-distilled a thread into a canonical topic and action item.
- Verified the topic file, topic index, pending-state transition, and optional close-thread path.
- Verified unresolved-distillation behavior can leave the source pending.

### Import workflow

- Ingested a text document into a temporary workspace.
- Verified:
  - original file copy,
  - normalized text with `txt-0001` anchor,
  - import record creation,
  - `imports.md` and `pending-distillation.md` updates.
- Edited import-record prose directly and ran `sync_import_state.py`.
- Deep-distilled the import into a canonical `Rover 3` topic.
- Verified the import became `complete` and the pending queue cleared.

## Skill Best-Practice Audit

### Satisfied

- Every user-facing skill has `SKILL.md`, `scripts/`, `references/`, and `evals/`.
- Skill names are lowercase hyphenated and match directory names.
- Descriptions are imperative and focus on user intent.
- Each skill has:
  - `Available scripts`
  - workflow guidance
  - a validation loop
  - a `Gotchas` section
  - concise `compatibility` metadata
- Skills reference support files using relative paths from the skill root.
- Shared guidance lives in `skills/shared/references/` instead of being duplicated.

### Remaining limits

- Trigger eval files and workflow eval files now exist, but no automated trigger-rate harness has been implemented yet.
- `timing.json`, `grading.json`, and `benchmark.json` are not committed artifacts; they are expected outputs of future eval runs.

## Product-Spec Coverage Audit

### Implemented bare functionality

- Immutable raw thread evidence capture.
- Rolling thread summaries and open-question tracking.
- Canonical action items and open-question records.
- Retrieval by topic/time/entity through a coarse query tool plus progressive disclosure.
- Workspace entrypoint and generated views.
- Deep distillation from threads into canonical topics and action items.
- Pending-distillation recovery surface.
- Document ingestion with normalized text and import records.
- Import-to-topic distillation path.

### Still primarily agent-driven rather than tool-enforced

- contradiction recognition and resolution quality,
- nuanced topic-selection quality,
- quality of historical change summaries,
- quality of final user-facing answer synthesis.

These are expected to remain agent-led. The current implementation provides the structural surfaces needed for them.

## Implementation-Spec Coverage Audit

### Implemented

- workspace bootstrap
- thread capture and sync
- canonical action-item storage and listing
- coarse retrieval helper
- canonical topic storage
- deep-distillation apply/finalize workflow
- import ingestion and import sync
- generated views and typed topic indexes
- basic locking for deep-distillation mutations
- per-skill eval fixture files

### Remaining gaps

- Lock coverage is not yet universal. Deep-distillation paths use lock files, but capture/sync/import paths do not yet enforce the same locking model.
- The skill-eval artifacts exist, but there is not yet a repo-local automation harness that repeatedly measures trigger rates and writes `grading.json`, `timing.json`, and `benchmark.json`.
- PDF ingestion depends on a local `pdftotext` tool and is not covered by the automated test suite.
