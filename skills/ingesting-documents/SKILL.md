---
name: ingesting-documents
description: Use this skill when the user wants to add an external document such as markdown, text, docx, or pdf into the workspace as evidence. It stages the source file, creates normalized text and an import record, then uses direct import-record edits plus structural follow-up for later deep distillation.
compatibility: Requires Python 3, a writable workspace root, and local PDF extraction support for pdf ingestion.
metadata:
  owner: ai-notes-2
---

# Ingesting Documents

Use this skill to turn an external document into durable workspace evidence without loading the full source into context unnecessarily.

Read `../shared/references/agent-script-boundary.md` before using this skill.
Read `references/ingestion-checklist.md` before ingesting a large source.
Read `../shared/references/citation-rules.md` before editing the import record summary.

## Available scripts

- `scripts/ingest_document.py` — copy/register the source, create normalized text, and create the import record
- `scripts/sync_import_state.py` — refresh import-record metadata and generated views after direct import-record edits

## Checklist

- ingest the source first
- read normalized text instead of the original binary when possible
- edit the import record directly
- sync structural state after the edit
- continue to deep distillation only if full reconciliation is needed now

## Workflow

1. Run `python scripts/ingest_document.py ...`.
2. Read the normalized text in `memory/imports/text/...`, not the original binary, unless the original artifact is required.
3. Edit the import record’s `## Source Summary`, `## Open Questions`, `## Candidate Action Items`, and `## Distillation Notes` directly.
4. If the document introduced explicit canonical action items, prepare the structured payload for them.
5. Run `python scripts/sync_import_state.py ...`.
6. By default, continue into `distilling-threads` if the user wants the import fully reconciled immediately.

## Validation Loop

- Confirm the original file, normalized text, and import record all exist.
- Confirm the import record preview matches the `## Source Summary`.
- Confirm `memory/views/imports.md` and `memory/views/pending-distillation.md` reflect the import.
- If canonical action items were passed, confirm they appear in `memory/views/action-items.md`.

## Gotchas

- Prefer normalized text over the original binary for reading and citation.
- The `## Source Summary` should be navigational, not exhaustive.
- `sync_import_state.py` does not summarize the document for you. Edit the import record first, then sync.
- `apply_import_update.py` is not required for the current workflow. Use direct edits plus `sync_import_state.py`.
